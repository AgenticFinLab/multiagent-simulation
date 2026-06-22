# GFC2008 / Leveraged Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GFC2008 |
| Agent type | Leveraged Investor |
| Canonical class | `LeveragedInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`LeveragedInvestor` represents highly leveraged balance sheets funded against structured-credit collateral. When price deviation breaches the margin trigger, it sells part of its position and amplifies the fall.

## Financial Theory / Theoretical Basis

### Rule / `LeveragedInvestor`
- Theory: simulation-bases.md Section 4.3 -- LeveragedInvestor
- Theoretical basis: Leverage cycle (Adrian & Shin, 2010).

### LLM / `LLMLeveragedInvestor`
- LLM-driven LeveragedInvestor: high leverage, forced to sell in downturn. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMLeveragedInvestor`
- RuleLLM-driven LeveragedInvestor: high leverage, forced to sell in downturn. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMLeveragedInvestor`
- RAG-augmented LeveragedInvestor: high leverage, forced to sell in downturn. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| buy_threshold | Rule: `-0.03`<br>LLM: `-0.03`<br>RuleLLM: `-0.03`<br>Rag: `-0.03` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fire_sale_fraction | Rule: `0.25`<br>LLM: `0.25`<br>RuleLLM: `0.25`<br>Rag: `0.25` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `1500`<br>LLM: `1500`<br>RuleLLM: `1500`<br>Rag: `1500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GFC2008.LLM.prompts:LLM_LEVERAGED_INVESTOR_SYS', 'user_message': 'examples.GFC2008.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_LEVERAGED_INVESTOR_SYS', 'user_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GFC2008.Rag.prompts:RAGLLM_LEVERAGED_INVESTOR_SYS', 'user_message': 'examples.GFC2008.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| margin_call_trigger | Rule: `0.1` | Rule |
| margin_trigger | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | leveragedinvestor | LeveragedInvestor | `LeveragedInvestor` | 2 | `examples/GFC2008/Rule/players.py` |
| LLM | leveragedinvestor | LeveragedInvestor | `LLMLeveragedInvestor` | 2 | `examples/GFC2008/LLM/players.py` |
| RuleLLM | leveragedinvestor | LeveragedInvestor | `RuleLLMLeveragedInvestor` | 2 | `examples/GFC2008/RuleLLM/players.py` |
| Rag | leveragedinvestor | LeveragedInvestor | `RagLLMLeveragedInvestor` | 2 | `examples/GFC2008/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 LeveragedInvestor

#### Section 4.3.1 Summary

`LeveragedInvestor` represents highly leveraged balance sheets funded against structured-credit collateral. When price deviation breaches the margin trigger, it sells part of its position and amplifies the fall.

#### Section 4.3.2 Theoretical and Empirical Foundation

The basis is Brunnermeier and Pedersen (2009) on funding-liquidity spirals and Adrian and Shin (2010) on procyclical leverage. The agent is the central fire-sale amplifier.

#### Section 4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < -margin_call_trigger` and position > 0 | sell half current position | forced deleveraging | Section 2 Theory 3 |
| otherwise | hold | leverage remains funded | Section 2 Theory 3 |

#### Section 4.3.4 Behavioral Framework

```
if deviation < -margin_call_trigger:
    sell int(position * 0.50)
else:
    hold
```

#### Section 4.3.5 Decision Process Walkthrough

With deviation -12% and `margin_call_trigger = 0.10`, the investor is forced to sell. The sale lowers price further through market impact.

#### Section 4.3.6 Worked Numerical Example

With 1,500 securities, the first fire-sale order is 750 units.

#### Section 4.3.7 Academic References

Brunnermeier & Pedersen (2009); Adrian & Shin (2010).

## Source Docstring Excerpts

### Rule / `LeveragedInvestor`

```text
Theory: simulation-bases.md Section 4.3 -- LeveragedInvestor

Theoretical basis: Leverage cycle (Adrian & Shin, 2010).
Uses high leverage; forced to sell in downturn (margin call / fire sale).
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMLeveragedInvestor`

```text
LLM-driven LeveragedInvestor: high leverage, forced to sell in downturn. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMLeveragedInvestor`

```text
RuleLLM-driven LeveragedInvestor: high leverage, forced to sell in downturn. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMLeveragedInvestor`

```text
RAG-augmented LeveragedInvestor: high leverage, forced to sell in downturn. Theory: simulation-bases.md Section 4.3.
```
