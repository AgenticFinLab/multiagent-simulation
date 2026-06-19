# CreditCycle / Value Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CreditCycle |
| Agent type | Value Investor |
| Canonical class | `ValueInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**4.4.1 Economic Role**: Fundamental-value anchor who buys undervalued and sells overvalued credit assets.

## Financial Theory / Theoretical Basis

### Rule / `ValueInvestor`
- Theory: simulation-bases.md Section 4.4 -- ValueInvestor
- Theoretical basis: Graham (1949) value investing with margin of safety; buys

### LLM / `LLMValueInvestor`
- LLM-driven value investor -- fundamental-anchored credit buyer at deep discount. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMValueInvestor`
- RuleLLM-driven value investor -- fundamental-anchored credit buyer at deep discount. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMValueInvestor`
- RAG-augmented value investor -- fundamental-anchored credit buyer at deep discount. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CreditCycle.LLM.prompts:LLM_VALUE_INVESTOR_SYS', 'user_message': 'examples.CreditCycle.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CreditCycle.RuleLLM.prompts:RULELLM_VALUE_INVESTOR_SYS', 'user_message': 'examples.CreditCycle.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CreditCycle.Rag.prompts:RAG_VALUE_INVESTOR_SYS', 'user_message': 'examples.CreditCycle.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `400` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| value_discount | Rule: `0.1`<br>LLM: `0.1`<br>RuleLLM: `0.1`<br>Rag: `0.1` | LLM, Rag, Rule, RuleLLM |
| value_premium | Rule: `0.1`<br>LLM: `0.1`<br>RuleLLM: `0.1`<br>Rag: `0.1` | LLM, Rag, Rule, RuleLLM |
| value_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | valueinvestor | ValueInvestor | `ValueInvestor` | 1 | `examples/CreditCycle/Rule/players.py` |
| LLM | valueinvestor | ValueInvestor | `LLMValueInvestor` | 1 | `examples/CreditCycle/LLM/players.py` |
| RuleLLM | valueinvestor | ValueInvestor | `RuleLLMValueInvestor` | 1 | `examples/CreditCycle/RuleLLM/players.py` |
| Rag | valueinvestor | ValueInvestor | `RagLLMValueInvestor` | 1 | `examples/CreditCycle/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ValueInvestor

**4.4.1 Economic Role**: Fundamental-value anchor who buys undervalued and sells overvalued credit assets.

**4.4.2 Destabilizing/Stabilizing**: Stabilizing -- provides mean-reversion force; buys deeply discounted assets during crises and sells overpriced assets during booms.

**4.4.3 Mathematical Model**:

```
qty(t) = order_size   if δ(t) < -value_discount   [buy -- undervalued]
qty(t) = order_size   if δ(t) > value_discount    [sell -- overvalued]
qty(t) = 0            otherwise
```

Parameters: `value_discount` = 0.10, `order_size` = 400.

**4.4.4 Calibration Targets**: Activates at >=10% discount/premium; stabilizes price within ±10% of fundamental over long run.

**4.4.5 Historical Analogue**: Distressed debt investors (Howard Marks / Oaktree) buying at crisis lows; fundamental-focused credit analysts reducing exposure at spread lows.

**4.4.6 Interaction Pattern**: Provides floor to CounterCyclicalLender's liquidity injection; sells into ProCyclicalLender's boom-phase buying.

**4.4.7 Diversity Contribution**: Anchors the market to fundamentals; its 10% threshold distinguishes it from smaller-threshold stabilizers.

---

## Source Docstring Excerpts

### Rule / `ValueInvestor`

```text
Invests based on fundamental value -- stabilizing force during credit expansions.

Theory: simulation-bases.md Section 4.4 -- ValueInvestor
Theoretical basis: Graham (1949) value investing with margin of safety; buys
deeply discounted credit assets and sells overpriced, anchoring price to fundamentals.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMValueInvestor`

```text
LLM-driven value investor -- fundamental-anchored credit buyer at deep discount. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMValueInvestor`

```text
RuleLLM-driven value investor -- fundamental-anchored credit buyer at deep discount. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMValueInvestor`

```text
RAG-augmented value investor -- fundamental-anchored credit buyer at deep discount. Theory: simulation-bases.md Section 4.4.
```
