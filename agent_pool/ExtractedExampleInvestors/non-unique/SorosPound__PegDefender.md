# SorosPound / Peg Defender

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SorosPound |
| Agent type | Peg Defender |
| Canonical class | `PegDefender` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A central-bank-style defender that intervenes to stabilize the currency proxy when deviation becomes large.

## Financial Theory / Theoretical Basis

### Rule / `PegDefender`
- Theory: simulation-bases.md Section 4.2

### LLM / `LLMPegDefender`
- Theory: simulation-bases.md Section 4.2

### RuleLLM / `RuleLLMPegDefender`
- Theory: simulation-bases.md Section 4.2

### Rag / `RagLLMPegDefender`
- Theory: simulation-bases.md Section 4.2

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| defense_size | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `95.0`<br>LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000000.0`<br>LLM: `10000000.0`<br>RuleLLM: `10000000.0`<br>Rag: `10000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SorosPound.LLM.prompts:LLM_PEG_DEFENDER_SYS', 'user_message': 'examples.SorosPound.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_PEG_DEFENDER_SYS', 'user_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SorosPound.Rag.prompts:RAGLLM_PEG_DEFENDER_SYS', 'user_message': 'examples.SorosPound.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| reserve_capacity | Rule: `0.8`<br>LLM: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | pegdefender | PegDefender | `PegDefender` | 1 | `examples/SorosPound/Rule/players.py` |
| LLM | pegdefender | PegDefender | `LLMPegDefender` | 1 | `examples/SorosPound/LLM/players.py` |
| RuleLLM | pegdefender | PegDefender | `RuleLLMPegDefender` | 1 | `examples/SorosPound/RuleLLM/players.py` |
| Rag | pegdefender | PegDefender | `RagLLMPegDefender` | 1 | `examples/SorosPound/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 PegDefender

**Summary**: A central-bank-style defender that intervenes to stabilize the
currency proxy when deviation becomes large.

**Theoretical and Empirical Basis**: The role represents exchange-market
intervention and policy commitment under reserve and political constraints.

**Design Purpose**: Provide stabilizing pressure that can offset attack flow but
is deliberately bounded.

**Behavioral Framework**: The retained Rule implementation activates when
`abs(deviation) > 0.05`, sizes `min(500, int(abs(deviation) * 3000))`, buys when
the proxy is below fundamental and sells when it is above.

**Decision Process**: Intervene only after a larger deviation than macro
attackers require, reflecting delayed and costly defense.

**Worked Numerical Example**: With deviation `-0.08`, the defender's raw support
quantity is `int(0.08 * 3000) = 240`; it buys up to 240 units if cash allows.

**Academic References**: Exchange-rate crisis literature on reserves, interest
rates, and credibility, including Obstfeld (1996).

## Source Docstring Excerpts

### Rule / `PegDefender`

```text
Peg defender.

Theory: simulation-bases.md Section 4.2
```

### LLM / `LLMPegDefender`

```text
LLM-driven peg defender.

Theory: simulation-bases.md Section 4.2
```

### RuleLLM / `RuleLLMPegDefender`

```text
RuleLLM peg defender.

Theory: simulation-bases.md Section 4.2
```

### Rag / `RagLLMPegDefender`

```text
RAG-augmented peg defender.

Theory: simulation-bases.md Section 4.2
```
