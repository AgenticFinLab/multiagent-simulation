# HerdingInformation / Reputation Herder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HerdingInformation |
| Agent type | Reputation Herder |
| Canonical class | `ReputationHerder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Scharfstein & Stein (1990) reputation/career-concern herding. Follows consensus direction to protect professional reputation. Lower activation threshold than CascadeFollower -- activates before full cascade lock-in.

## Financial Theory / Theoretical Basis

### Rule / `ReputationHerder`
- Theory: simulation-bases.md Section 4.2 -- ReputationHerder
- Theoretical basis: Reputation-based herding (Scharfstein & Stein, 1990).

### LLM / `LLMReputationHerder`
- LLM-driven reputation-based herder. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMReputationHerder`
- RuleLLM-driven reputation-based herder. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMReputationHerder`
- RagLLM-driven reputation-based herder. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HerdingInformation.LLM.prompts:LLM_REPUTATION_HERDER_SYS', 'user_message': 'examples.HerdingInformation.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.HerdingInformation.RuleLLM.prompts:RULELLM_REPUTATION_HERDER_SYS', 'user_message': 'examples.HerdingInformation.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.HerdingInformation.Rag.prompts:RAGLLM_REPUTATION_HERDER_SYS', 'user_message': 'examples.HerdingInformation.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| reputation_concern | Rule: `0.7`<br>LLM: `0.7`<br>RuleLLM: `0.7`<br>Rag: `0.7` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | reputationherder | ReputationHerder | `ReputationHerder` | 3 | `examples/HerdingInformation/Rule/players.py` |
| LLM | reputationherder | ReputationHerder | `LLMReputationHerder` | 3 | `examples/HerdingInformation/LLM/players.py` |
| RuleLLM | reputationherder | ReputationHerder | `RuleLLMReputationHerder` | 3 | `examples/HerdingInformation/RuleLLM/players.py` |
| Rag | reputationherder | ReputationHerder | `RagLLMReputationHerder` | 3 | `examples/HerdingInformation/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 ReputationHerder

**Summary**: Implements Scharfstein & Stein (1990) reputation/career-concern herding. Follows consensus direction to protect professional reputation. Lower activation threshold than CascadeFollower -- activates before full cascade lock-in.

**Foundation**: Scharfstein & Stein (1990); Chevalier & Ellison (1999) career-concern evidence.

**Design Purpose**: Represent the "pre-cascade" herding force from career incentives. Activates at any |deviation| > 0.02 -- does not require the sustained evidence that CascadeFollower needs. Creates compounded herding coalition with CascadeFollower.

**Behavioral Framework**:

| Decision Variable    | Logic                                                | Formula                |
|----------------------|------------------------------------------------------|------------------------|
| Activation threshold | Lower than CascadeFollower                           | `abs(deviation) > 0.02` |
| Trade size           | Proportional to deviation x reputation amplification | `min(600, int(abs(dev) x reputation_concern x 4000))` |
| Direction            | Follow deviation direction                           | Consensus follower     |
| reputation_concern   | Career pressure intensity                            | 0.7 config             |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. If `|deviation| > 0.02`: trade
3. `qty = min(600, int(|dev| x reputation_concern x 4000))`; direction = sign(deviation)

**Worked Example** (reputation_concern=0.7, deviation=+0.04):
- `|0.04| > 0.02` -> activates
- qty = min(600, int(0.04 x 0.7 x 4000)) = min(600, 112) = 112
- Action: buy 112 shares -- reputation herding

**References**: simulation-bases.md Section 2 Theory 2; `doi:10.2307/2006957`

---

## Source Docstring Excerpts

### Rule / `ReputationHerder`

```text
Theory: simulation-bases.md Section 4.2 -- ReputationHerder

Theoretical basis: Reputation-based herding (Scharfstein & Stein, 1990).
Reputation herder: follows consensus to protect professional reputation.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMReputationHerder`

```text
LLM-driven reputation-based herder. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMReputationHerder`

```text
RuleLLM-driven reputation-based herder. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMReputationHerder`

```text
RagLLM-driven reputation-based herder. Theory: simulation-bases.md Section 4.2.
```
