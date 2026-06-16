# EuropeanDebtCrisis / Core Bond Buyer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EuropeanDebtCrisis |
| Agent type | Core Bond Buyer |
| Canonical class | `CoreBondBuyer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `CoreBondBuyer` represents flight-to-quality capital reallocating toward safer core assets. In the normalized periphery market, it buys during stress and sells after recovery, modelling safe-asset rotation pressure.

## Financial Theory / Theoretical Basis

### Rule / `CoreBondBuyer`
- Theory: simulation-bases.md Section 4.3 -- CoreBondBuyer
- Theoretical basis: De Grauwe & Ji (2012) flight-to-safety; capital rotation

### LLM / `LLMCoreBondBuyer`
- LLM-driven core bond buyer -- flight-to-quality capital rotation via LLM reasoning. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMCoreBondBuyer`
- RuleLLM core bond buyer -- flight-to-quality rules with LLM safe-haven reasoning. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMCoreBondBuyer`
- RAG-augmented core bond buyer -- flight-to-quality with safe-haven literature. Theory: simulation-bases.md Section 4.3.

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
| flight_threshold | Rule: `-0.08` | Rule |
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_CORE_BOND_BUYER_SYS', 'user_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_CORE_BOND_BUYER_SYS', 'user_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_CORE_BOND_BUYER_SYS', 'user_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| value_threshold | LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | corebondbuyer | CoreBondBuyer | `CoreBondBuyer` | 1 | `examples/EuropeanDebtCrisis/Rule/players.py` |
| LLM | corebondbuyer | CoreBondBuyer | `LLMCoreBondBuyer` | 1 | `examples/EuropeanDebtCrisis/LLM/players.py` |
| RuleLLM | corebondbuyer | CoreBondBuyer | `RuleLLMCoreBondBuyer` | 1 | `examples/EuropeanDebtCrisis/RuleLLM/players.py` |
| Rag | corebondbuyer | CoreBondBuyer | `RagLLMCoreBondBuyer` | 1 | `examples/EuropeanDebtCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 CoreBondBuyer

#### Section 4.3.1 Summary

The `CoreBondBuyer` represents flight-to-quality capital reallocating toward safer core assets. In the normalized periphery market, it buys during stress and sells after recovery, modelling safe-asset rotation pressure.

#### Section 4.3.2 Theoretical and Empirical Foundation

The basis is eurozone flight-to-safety evidence (Section 2.3) and safe-asset demand. The agent is not a panicker; it reacts to stress by seeking safer exposure.

#### Section 4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < flight_threshold` | buy | represents crisis-driven safety demand in the normalized bond index | Section 2.3 |
| `deviation > 0.10` | sell | reduces safe-haven allocation after recovery | Section 2.3 |

#### Section 4.3.4 Behavioral Framework

```
if deviation < flight_threshold: buy min(400, cash / price)
elif deviation > 0.10: sell min(400, position)
else: hold
```

#### Section 4.3.5 Decision Process Walkthrough

At deviation -12% with `flight_threshold = -8%`, the agent buys the safety proxy.

#### Section 4.3.6 Worked Numerical Example

With cash 1,000,000 and price 88, affordable quantity is above 400, so order quantity is 400.

#### Section 4.3.7 Academic References

De Grauwe & Ji (2013); Krishnamurthy & Vissing-Jorgensen (2012).

## Source Docstring Excerpts

### Rule / `CoreBondBuyer`

```text
Buys core sovereign bonds as flight-to-quality, compressing core yields.

Theory: simulation-bases.md Section 4.3 -- CoreBondBuyer
Theoretical basis: De Grauwe & Ji (2012) flight-to-safety; capital rotation
from periphery to core bonds indirectly deepens the periphery crisis.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMCoreBondBuyer`

```text
LLM-driven core bond buyer -- flight-to-quality capital rotation via LLM reasoning. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMCoreBondBuyer`

```text
RuleLLM core bond buyer -- flight-to-quality rules with LLM safe-haven reasoning. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMCoreBondBuyer`

```text
RAG-augmented core bond buyer -- flight-to-quality with safe-haven literature. Theory: simulation-bases.md Section 4.3.
```
