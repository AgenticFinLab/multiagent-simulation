# SouthSeaBubble / Arbitrageur

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SouthSeaBubble |
| Agent type | Arbitrageur |
| Canonical class | `Arbitrageur` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A sophisticated trader attempting to exploit gaps between narrative price and fundamental value. **Theoretical and Empirical Basis**: Limits-to-arbitrage theory. **Design Purpose**: Add correction pressure without assuming unlimited capital. **Behavioral Framework**: Uses the same retained 5% activation threshold and 500-unit cap as skeptical analysts. **Decision Process**: Buy underpricing and sell overpricing, constrained by cash and current inventory. **Worked Numerical Example**: At deviation `-0.08`, raw buy quantity is 240. **Academic References**: Shleifer and Vishny (1997).

## Financial Theory / Theoretical Basis

### Rule / `Arbitrageur`
- Theory: simulation-bases.md Section 4.4

### LLM / `LLMArbitrageur`
- Theory: simulation-bases.md Section 4.4

### RuleLLM / `RuleLLMArbitrageur`
- Theory: simulation-bases.md Section 4.4

### Rag / `RagLLMArbitrageur`
- Theory: simulation-bases.md Section 4.4

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
| initial_position | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SouthSeaBubble.LLM.prompts:LLM_ARBITRAGEUR_SYS', 'user_message': 'examples.SouthSeaBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SouthSeaBubble.RuleLLM.prompts:RULELLM_ARBITRAGEUR_SYS', 'user_message': 'examples.SouthSeaBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SouthSeaBubble.Rag.prompts:RAGLLM_ARBITRAGEUR_SYS', 'user_message': 'examples.SouthSeaBubble.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| spread_threshold | Rule: `0.25`<br>LLM: `0.25`<br>RuleLLM: `0.25`<br>Rag: `0.25` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | arbitrageur | Arbitrageur | `Arbitrageur` | 2 | `examples/SouthSeaBubble/Rule/players.py` |
| LLM | arbitrageur | Arbitrageur | `LLMArbitrageur` | 2 | `examples/SouthSeaBubble/LLM/players.py` |
| RuleLLM | arbitrageur | Arbitrageur | `RuleLLMArbitrageur` | 2 | `examples/SouthSeaBubble/RuleLLM/players.py` |
| Rag | arbitrageur | Arbitrageur | `RagLLMArbitrageur` | 2 | `examples/SouthSeaBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 Arbitrageur

**Summary**: A sophisticated trader attempting to exploit gaps between narrative
price and fundamental value.
**Theoretical and Empirical Basis**: Limits-to-arbitrage theory.
**Design Purpose**: Add correction pressure without assuming unlimited capital.
**Behavioral Framework**: Uses the same retained 5% activation threshold and
500-unit cap as skeptical analysts.
**Decision Process**: Buy underpricing and sell overpricing, constrained by cash
and current inventory.
**Worked Numerical Example**: At deviation `-0.08`, raw buy quantity is 240.
**Academic References**: Shleifer and Vishny (1997).

## Source Docstring Excerpts

### Rule / `Arbitrageur`

```text
Arbitrageur against narrative mispricing.

Theory: simulation-bases.md Section 4.4
```

### LLM / `LLMArbitrageur`

```text
LLM-driven arbitrageur.

Theory: simulation-bases.md Section 4.4
```

### RuleLLM / `RuleLLMArbitrageur`

```text
Rule+LLM arbitrageur exploiting narrative vs fundamental gap.

Theory: simulation-bases.md Section 4.4
```

### Rag / `RagLLMArbitrageur`

```text
RAG-augmented arbitrageur exploiting narrative vs fundamental gap.

Theory: simulation-bases.md Section 4.4
```
