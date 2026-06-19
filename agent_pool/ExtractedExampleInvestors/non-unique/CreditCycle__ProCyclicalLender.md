# CreditCycle / Pro Cyclical Lender

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CreditCycle |
| Agent type | Pro Cyclical Lender |
| Canonical class | `ProCyclicalLender` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**4.1.1 Economic Role**: Pro-cyclical credit supplier whose lending standards move with asset prices.

## Financial Theory / Theoretical Basis

### Rule / `ProCyclicalLender`
- Theory: simulation-bases.md Section 4.1 -- ProCyclicalLender
- Theoretical basis: Adrian & Shin (2010) pro-cyclical leverage; lending standards

### LLM / `LLMProCyclicalLender`
- LLM-driven pro-cyclical lender -- expands credit in booms, tightens in busts. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMProCyclicalLender`
- RuleLLM-driven pro-cyclical lender -- expands credit in booms, tightens in busts. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMProCyclicalLender`
- RAG-augmented pro-cyclical lender -- expands credit in booms, tightens in busts. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| contraction_threshold | Rule: `-0.015`<br>LLM: `-0.015`<br>RuleLLM: `-0.015`<br>Rag: `-0.015` | LLM, Rag, Rule, RuleLLM |
| credit_multiplier | Rule: `2.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| expansion_threshold | Rule: `0.01`<br>LLM: `0.01`<br>RuleLLM: `0.01`<br>Rag: `0.01` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| leverage_contraction_rate | Rule: `0.4`<br>LLM: `0.4`<br>RuleLLM: `0.4`<br>Rag: `0.4` | LLM, Rag, Rule, RuleLLM |
| leverage_expansion_rate | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CreditCycle.LLM.prompts:LLM_PRO_CYCLICAL_LENDER_SYS', 'user_message': 'examples.CreditCycle.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CreditCycle.RuleLLM.prompts:RULELLM_PRO_CYCLICAL_LENDER_SYS', 'user_message': 'examples.CreditCycle.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CreditCycle.Rag.prompts:RAG_PRO_CYCLICAL_LENDER_SYS', 'user_message': 'examples.CreditCycle.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `600` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | procyclicallender | ProCyclicalLender | `ProCyclicalLender` | 2 | `examples/CreditCycle/Rule/players.py` |
| LLM | procyclicallender | ProCyclicalLender | `LLMProCyclicalLender` | 2 | `examples/CreditCycle/LLM/players.py` |
| RuleLLM | procyclicallender | ProCyclicalLender | `RuleLLMProCyclicalLender` | 2 | `examples/CreditCycle/RuleLLM/players.py` |
| Rag | procyclicallender | ProCyclicalLender | `RagLLMProCyclicalLender` | 2 | `examples/CreditCycle/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 ProCyclicalLender

**4.1.1 Economic Role**: Pro-cyclical credit supplier whose lending standards move with asset prices.

**4.1.2 Destabilizing/Stabilizing**: Destabilizing -- amplifies booms by expanding credit when prices rise, amplifies busts by contracting credit when prices fall.

**4.1.3 Mathematical Model**:

```
qty(t) = order_size x credit_multiplier   if δ(t) > expansion_threshold  [buy/lend]
qty(t) = order_size                        if δ(t) < -expansion_threshold [sell/withdraw]
qty(t) = 0                                otherwise
```

Parameters: `expansion_threshold` = 0.01, `contraction_threshold` = -0.015, `credit_multiplier` = 2.0, `order_size` = 600.

**4.1.4 Calibration Targets**: Peak buy volume ≈ 1,200 units/round during boom phase; sell volume ≈ 600 during bust onset.

**4.1.5 Historical Analogue**: US bank lending 2004-2007 (expanding subprime credit with rising house prices); abrupt tightening post-2008.

**4.1.6 Interaction Pattern**: Reinforces MinskyBorrower buying during boom; competes with CounterCyclicalLender during bust; amplifies deviation from fundamental.

**4.1.7 Diversity Contribution**: Provides the primary credit acceleration mechanism; distinguishes boom-bust amplification from pure noise.

---

## Source Docstring Excerpts

### Rule / `ProCyclicalLender`

```text
Expands credit during booms, tightens during downturns -- amplifies credit cycle.

Theory: simulation-bases.md Section 4.1 -- ProCyclicalLender
Theoretical basis: Adrian & Shin (2010) pro-cyclical leverage; lending standards
loosen with rising asset prices and tighten when prices fall, amplifying the cycle.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMProCyclicalLender`

```text
LLM-driven pro-cyclical lender -- expands credit in booms, tightens in busts. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMProCyclicalLender`

```text
RuleLLM-driven pro-cyclical lender -- expands credit in booms, tightens in busts. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMProCyclicalLender`

```text
RAG-augmented pro-cyclical lender -- expands credit in booms, tightens in busts. Theory: simulation-bases.md Section 4.1.
```
