# SVBBankRun / Bond Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SVBBankRun |
| Agent type | Bond Trader |
| Canonical class | `BondTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trades the proxy based on rate-sensitive asset valuation. **Theoretical and Empirical Foundation**: Fixed-income duration and mark-to-market loss transmission. **Design Purpose and Activation Scenarios**: Reacts when `abs(deviation) > 0.03`. **Behavioral Framework**: Opportunistic rates specialist; buys undervaluation and sells overvaluation. **Mathematical Model**: ``` qty = min(500, floor(abs(deviation) x 3000)) buy if deviation < 0, sell if deviation > 0 ``` **Decision Process Walkthrough**: Convert valuation deviation into bounded directional pressure. **Worked Example**: `deviation=-0.07` yields `qty=210`; the trader buys if cash permits. **References**: Fixed-income duration and crisis mark-to-market literature.

## Financial Theory / Theoretical Basis

### Rule / `BondTrader`
- Theory: simulation-bases.md Section 4.5 -- BondTrader
- Theoretical basis: fixed-income duration and mark-to-market losses.

### LLM / `LLMBondTrader`
- LLM-driven bond trader based on interest rate expectations. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMBondTrader`
- Hybrid Rule+LLM bond trader with fixed income rules. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMBondTrader`
- RAG-augmented bond trader with fixed income rules and retrieved knowledge. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SVBBankRun.LLM.prompts:LLM_BOND_TRADER_SYS', 'user_message': 'examples.SVBBankRun.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_BOND_TRADER_SYS', 'user_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SVBBankRun.Rag.prompts:RAGLLM_BOND_TRADER_SYS', 'user_message': 'examples.SVBBankRun.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |
| yield_sensitivity | Rule: `0.5`<br>LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | bondtrader | BondTrader | `BondTrader` | 2 | `examples/SVBBankRun/Rule/players.py` |
| LLM | bondtrader | BondTrader | `LLMBondTrader` | 2 | `examples/SVBBankRun/LLM/players.py` |
| RuleLLM | bondtrader | BondTrader | `RuleLLMBondTrader` | 2 | `examples/SVBBankRun/RuleLLM/players.py` |
| Rag | bondtrader | BondTrader | `RagLLMBondTrader` | 2 | `examples/SVBBankRun/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 BondTrader

**Summary**: Trades the proxy based on rate-sensitive asset valuation.
**Theoretical and Empirical Foundation**: Fixed-income duration and mark-to-market loss transmission.
**Design Purpose and Activation Scenarios**: Reacts when `abs(deviation) > 0.03`.
**Behavioral Framework**: Opportunistic rates specialist; buys undervaluation and sells overvaluation.
**Mathematical Model**:
```
qty = min(500, floor(abs(deviation) x 3000))
buy if deviation < 0, sell if deviation > 0
```
**Decision Process Walkthrough**: Convert valuation deviation into bounded directional pressure.
**Worked Example**: `deviation=-0.07` yields `qty=210`; the trader buys if cash permits.
**References**: Fixed-income duration and crisis mark-to-market literature.

## Source Docstring Excerpts

### Rule / `BondTrader`

```text
Bond trader who reprices bank exposure from duration-loss signals.

Theory: simulation-bases.md Section 4.5 -- BondTrader
Theoretical basis: fixed-income duration and mark-to-market losses.
See simulation-bases.md Section 4.5 for the bond-loss pressure rule.

Parameters from config extras: (none specific)
```

### LLM / `LLMBondTrader`

```text
LLM-driven bond trader based on interest rate expectations. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMBondTrader`

```text
Hybrid Rule+LLM bond trader with fixed income rules. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMBondTrader`

```text
RAG-augmented bond trader with fixed income rules and retrieved knowledge. Theory: simulation-bases.md Section 4.5.
```
