# SorosPound / Macro Hedge Fund

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SorosPound |
| Agent type | Macro Hedge Fund |
| Canonical class | `MacroHedgeFund` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A global macro speculator that attacks a peg when misalignment is large enough to justify a directional position.

## Financial Theory / Theoretical Basis

### Rule / `MacroHedgeFund`
- Theory: simulation-bases.md Section 4.1

### LLM / `LLMMacroHedgeFund`
- Theory: simulation-bases.md Section 4.1

### RuleLLM / `RuleLLMMacroHedgeFund`
- Theory: simulation-bases.md Section 4.1

### Rag / `RagLLMMacroHedgeFund`
- Theory: simulation-bases.md Section 4.1

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `95.0`<br>LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `5000000.0`<br>LLM: `5000000.0`<br>RuleLLM: `5000000.0`<br>Rag: `5000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `800`<br>LLM: `800`<br>RuleLLM: `800`<br>Rag: `800` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| leverage | Rule: `3.0`<br>LLM: `3.0`<br>RuleLLM: `3.0`<br>Rag: `3.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SorosPound.LLM.prompts:LLM_MACRO_HEDGE_FUND_SYS', 'user_message': 'examples.SorosPound.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_MACRO_HEDGE_FUND_SYS', 'user_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SorosPound.Rag.prompts:RAGLLM_MACRO_HEDGE_FUND_SYS', 'user_message': 'examples.SorosPound.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | macrohedgefund | MacroHedgeFund | `MacroHedgeFund` | 2 | `examples/SorosPound/Rule/players.py` |
| LLM | macrohedgefund | MacroHedgeFund | `LLMMacroHedgeFund` | 2 | `examples/SorosPound/LLM/players.py` |
| RuleLLM | macrohedgefund | MacroHedgeFund | `RuleLLMMacroHedgeFund` | 2 | `examples/SorosPound/RuleLLM/players.py` |
| Rag | macrohedgefund | MacroHedgeFund | `RagLLMMacroHedgeFund` | 2 | `examples/SorosPound/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 MacroHedgeFund

**Summary**: A global macro speculator that attacks a peg when misalignment is
large enough to justify a directional position.

**Theoretical and Empirical Basis**: The role represents informed speculative
pressure in first- and second-generation currency crisis models, and is the
scenario's George Soros-style attacker.

**Design Purpose**: Provide large, destabilizing order flow when the currency
proxy departs from fundamental value.

**Behavioral Framework**: The retained Rule implementation activates when
`abs(deviation) > 0.02`, sizes `min(800, int(abs(deviation) * 5000))`, buys when
the proxy is above fundamental and sells when it is below, subject to cash and
inventory constraints.

**Decision Process**: Read current `price`, `fundamental`, `deviation`, `cash`,
and `position`; if the deviation threshold is not reached, hold; otherwise
submit the bounded directional quantity.

**Worked Numerical Example**: With deviation `+0.06`, the raw attack quantity is
`int(0.06 * 5000) = 300`; the macro fund buys up to 300 units if it has enough
cash at the current proxy price.

**Academic References**: Krugman (1979), Flood and Garber (1984), and Obstfeld
(1996).

## Source Docstring Excerpts

### Rule / `MacroHedgeFund`

```text
Macro speculative attacker.

Theory: simulation-bases.md Section 4.1
```

### LLM / `LLMMacroHedgeFund`

```text
LLM-driven macro hedge fund.

Theory: simulation-bases.md Section 4.1
```

### RuleLLM / `RuleLLMMacroHedgeFund`

```text
RuleLLM macro hedge fund.

Theory: simulation-bases.md Section 4.1
```

### Rag / `RagLLMMacroHedgeFund`

```text
RAG-augmented macro hedge fund.

Theory: simulation-bases.md Section 4.1
```
