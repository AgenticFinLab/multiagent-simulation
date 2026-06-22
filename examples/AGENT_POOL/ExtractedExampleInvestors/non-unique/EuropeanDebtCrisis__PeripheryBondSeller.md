# EuropeanDebtCrisis / Periphery Bond Seller

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EuropeanDebtCrisis |
| Agent type | Periphery Bond Seller |
| Canonical class | `PeripheryBondSeller` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `PeripheryBondSeller` represents investors selling peripheral sovereign debt when market stress appears. It is the first crisis amplifier because selling lowers bond prices and raises implied yields.

## Financial Theory / Theoretical Basis

### Rule / `PeripheryBondSeller`
- Theory: simulation-bases.md Section 4.1 -- PeripheryBondSeller
- Theoretical basis: De Grauwe (2011) self-fulfilling speculation; speculative

### LLM / `LLMPeripheryBondSeller`
- LLM-driven periphery bond seller -- speculative selling amplifies yield spreads. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMPeripheryBondSeller`
- RuleLLM periphery bond seller -- explicit spread threshold rules with LLM crisis narrative. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMPeripheryBondSeller`
- RAG-augmented periphery bond seller -- speculative selling with sovereign crisis literature. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| core_price | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_PERIPHERY_BOND_SELLER_SYS', 'user_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_PERIPHERY_BOND_SELLER_SYS', 'user_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_PERIPHERY_BOND_SELLER_SYS', 'user_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| panic_threshold | LLM: `5.0`<br>RuleLLM: `5.0`<br>Rag: `5.0` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sell_threshold | Rule: `-0.1` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | peripherybondseller | PeripheryBondSeller | `PeripheryBondSeller` | 2 | `examples/EuropeanDebtCrisis/Rule/players.py` |
| LLM | peripherybondseller | PeripheryBondSeller | `LLMPeripheryBondSeller` | 2 | `examples/EuropeanDebtCrisis/LLM/players.py` |
| RuleLLM | peripherybondseller | PeripheryBondSeller | `RuleLLMPeripheryBondSeller` | 2 | `examples/EuropeanDebtCrisis/RuleLLM/players.py` |
| Rag | peripherybondseller | PeripheryBondSeller | `RagLLMPeripheryBondSeller` | 2 | `examples/EuropeanDebtCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 PeripheryBondSeller

#### Section 4.1.1 Summary

The `PeripheryBondSeller` represents investors selling peripheral sovereign debt when market stress appears. It is the first crisis amplifier because selling lowers bond prices and raises implied yields.

#### Section 4.1.2 Theoretical and Empirical Foundation

The agent follows self-fulfilling crisis logic from De Grauwe (Section 2.1). De Grauwe and Ji's spread evidence supports the idea that selling can occur beyond what fiscal fundamentals alone explain.

#### Section 4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < sell_threshold` | sell | amplifies peripheral spread pressure | Section 2.1 |
| `deviation > 0.08` | buy | returns when crisis abates | Section 2.1 |

#### Section 4.1.4 Behavioral Framework

```
if deviation < sell_threshold: sell min(600, position)
elif deviation > 0.08: buy min(400, cash / price)
else: hold
```

Information set: price, fundamental, deviation, cash, and position.

#### Section 4.1.5 Decision Process Walkthrough

At price 85 and fundamental 100, deviation is -15%. If `sell_threshold = -10%`, the seller liquidates because the stress signal has crossed its mandate threshold.

#### Section 4.1.6 Worked Numerical Example

With position 500 and sell cap 600, sell quantity is `min(600, 500) = 500`.

#### Section 4.1.7 Academic References

De Grauwe (2011); De Grauwe & Ji (2013).

## Source Docstring Excerpts

### Rule / `PeripheryBondSeller`

```text
Sells periphery sovereign bonds on risk signals, amplifying yield spreads.

Theory: simulation-bases.md Section 4.1 -- PeripheryBondSeller
Theoretical basis: De Grauwe (2011) self-fulfilling speculation; speculative
selling on negative signals amplifies price falls in a reflexive crisis loop.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMPeripheryBondSeller`

```text
LLM-driven periphery bond seller -- speculative selling amplifies yield spreads. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMPeripheryBondSeller`

```text
RuleLLM periphery bond seller -- explicit spread threshold rules with LLM crisis narrative. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMPeripheryBondSeller`

```text
RAG-augmented periphery bond seller -- speculative selling with sovereign crisis literature. Theory: simulation-bases.md Section 4.1.
```
