# DotComBubble / IPO Flipper

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DotComBubble |
| Agent type | IPO Flipper |
| Canonical class | `IPOFlipper` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

Short-horizon trader who buys below fundamental and sells after a price pop. It adds speculative turnover and can create selling pressure near the top.

## Financial Theory / Theoretical Basis

### Rule / `IPOFlipper`
- Theory: simulation-bases.md Section 4.2 -- IPOFlipper
- Theoretical basis: Ofek & Richardson (2003) IPO dynamics; Ritter (1991) underpricing and flipping.

### LLM / `LLMIPOFlipper`
- LLM-driven IPO flipper -- buys at dip, sells on pop for short-term profit. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMIPOFlipper`
- RuleLLM-driven IPO flipper -- flip threshold rules embedded. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMIPOFlipper`
- RAG-augmented IPO flipper -- short-term flip strategy with historical IPO knowledge. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| entry_threshold | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |
| flip_return | Rule: `0.15`<br>LLM: `0.15`<br>RuleLLM: `0.15`<br>Rag: `0.15` | LLM, Rag, Rule, RuleLLM |
| flip_threshold | Rule: `0.05` | Rule |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DotComBubble.LLM.prompts:LLM_IPO_FLIPPER_SYS', 'user_message': 'examples.DotComBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_IPO_FLIPPER_SYS', 'user_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.DotComBubble.Rag.prompts:RAG_IPO_FLIPPER_SYS', 'user_message': 'examples.DotComBubble.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `700` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | ipoflipper | IPOFlipper | `IPOFlipper` | 2 | `examples/DotComBubble/Rule/players.py` |
| LLM | ipoflipper | IPOFlipper | `LLMIPOFlipper` | 2 | `examples/DotComBubble/LLM/players.py` |
| RuleLLM | ipoflipper | IPOFlipper | `RuleLLMIPOFlipper` | 2 | `examples/DotComBubble/RuleLLM/players.py` |
| Rag | ipoflipper | IPOFlipper | `RagLLMIPOFlipper` | 2 | `examples/DotComBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 IPOFlipper

#### Section 4.2.1 Summary

Short-horizon trader who buys below fundamental and sells after a price pop. It adds speculative turnover and can create selling pressure near the top.

#### Section 4.2.2 Theoretical and Empirical Foundation

The basis is IPO underpricing and post-issuance reversal (Section 2.2). The dot-com IPO market created incentives to buy allocation-like dips and sell into initial enthusiasm.

#### Section 4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > flip_threshold` | sell up to `order_size` | profit taking above fundamental | Section 2.2 |
| `deviation < 0` | buy up to `order_size` | inventory for next flip | Section 2.2 |

#### Section 4.2.4 Behavioral Framework

```
if deviation > flip_threshold and position > 0: sell min(order_size, position)
elif deviation < 0: buy min(order_size, cash / price)
else: hold
```

#### Section 4.2.5 Decision Process Walkthrough

At price 108 and fundamental 100 with `flip_threshold = 0.05`, the flipper sells because the pop exceeds 5%.

#### Section 4.2.6 Worked Numerical Example

With position 500 and `order_size = 700`, sell quantity is `min(700, 500) = 500`.

#### Section 4.2.7 Academic References

Ofek & Richardson (2003); Ritter (1991).

## Source Docstring Excerpts

### Rule / `IPOFlipper`

```text
Buys IPOs and quickly sells for short-term profit.

Theory: simulation-bases.md Section 4.2 -- IPOFlipper
Theoretical basis: Ofek & Richardson (2003) IPO dynamics; Ritter (1991) underpricing and flipping.
See simulation-bases.md Section 4.2 for mathematical model.
Role: destabilizing.
```

### LLM / `LLMIPOFlipper`

```text
LLM-driven IPO flipper -- buys at dip, sells on pop for short-term profit. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMIPOFlipper`

```text
RuleLLM-driven IPO flipper -- flip threshold rules embedded. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMIPOFlipper`

```text
RAG-augmented IPO flipper -- short-term flip strategy with historical IPO knowledge. Theory: simulation-bases.md Section 4.2.
```
