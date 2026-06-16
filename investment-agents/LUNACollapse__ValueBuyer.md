# LUNACollapse / Value Buyer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LUNACollapse |
| Agent type | Value Buyer |
| Canonical class | `ValueBuyer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A contrarian buyer that attempts to buy deep discounts but is often too small to stop the spiral.

## Financial Theory / Theoretical Basis

### Rule / `ValueBuyer`
- Theory: simulation-bases.md Section 4.5 -- ValueBuyer
- Theoretical Basis: Mean reversion / fundamental value investing

### LLM / `LLMValueBuyer`
- LLM-driven contrarian value buyer. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMValueBuyer`
- RuleLLM contrarian value buyer. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMValueBuyer`
- RAG contrarian value buyer. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `200`<br>LLM: `200`<br>RuleLLM: `200`<br>Rag: `200` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| discount_threshold | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `3000000.0`<br>LLM: `3000000.0`<br>RuleLLM: `3000000.0`<br>Rag: `3000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `200`<br>LLM: `200`<br>RuleLLM: `200`<br>Rag: `200` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LUNACollapse.LLM.prompts:LLM_VALUEBUYER_PROMPT', 'user_message': 'examples.LUNACollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_VALUEBUYER_PROMPT', 'user_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LUNACollapse.Rag.prompts:RAG_VALUEBUYER_PROMPT', 'user_message': 'examples.LUNACollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | valuebuyer | ValueBuyer | `ValueBuyer` | 1 | `examples/LUNACollapse/Rule/players.py` |
| LLM | valuebuyer | ValueBuyer | `LLMValueBuyer` | 1 | `examples/LUNACollapse/LLM/players.py` |
| RuleLLM | valuebuyer | ValueBuyer | `RuleLLMValueBuyer` | 1 | `examples/LUNACollapse/RuleLLM/players.py` |
| Rag | valuebuyer | ValueBuyer | `RagLLMValueBuyer` | 1 | `examples/LUNACollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 ValueBuyer

**Summary**: A contrarian buyer that attempts to buy deep discounts but is often
too small to stop the spiral.

**Theoretical and Empirical Basis**: Limits-of-arbitrage theory explains why
value buyers may be overwhelmed during funding stress.

**Design Purpose**: Provide a stabilizing force and test whether it can absorb
panic selling.

**Behavioral Framework**: Buys when `deviation < -discount_threshold`.

**Decision Process**: If discount is deep enough, buy cash-constrained quantity;
otherwise hold.

**Worked Numerical Example**: With `discount_threshold = 0.30`, the buyer waits
for a 30% discount before deploying capital.

**Academic References**: Shleifer and Vishny (1997); crisis arbitrage evidence.

## Source Docstring Excerpts

### Rule / `ValueBuyer`

```text
Contrarian value investor attempting to buy at deep discount.

Theory: simulation-bases.md Section 4.5 -- ValueBuyer
Theoretical Basis: Mean reversion / fundamental value investing
Market Role: stabilizing -- but overwhelmed by selling pressure in crisis
```

### LLM / `LLMValueBuyer`

```text
LLM-driven contrarian value buyer. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMValueBuyer`

```text
RuleLLM contrarian value buyer. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMValueBuyer`

```text
RAG contrarian value buyer. Theory: simulation-bases.md Section 4.5.
```
