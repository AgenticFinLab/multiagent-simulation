# HerdingInformation / Cascade Follower

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HerdingInformation |
| Agent type | Cascade Follower |
| Canonical class | `CascadeFollower` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Bikhchandani et al. (1992) information cascade model. Ignores private signal once cascade_count reaches cascade_trigger threshold. Primary cascade amplifier -- follows deviation direction unconditionally after lock-in.

## Financial Theory / Theoretical Basis

### Rule / `CascadeFollower`
- Theory: simulation-bases.md Section 4.1 -- CascadeFollower
- Theoretical basis: Information cascade theory (Bikhchandani et al., 1992).

### LLM / `LLMCascadeFollower`
- LLM-driven information cascade follower. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMCascadeFollower`
- RuleLLM-driven information cascade follower. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMCascadeFollower`
- RagLLM-driven information cascade follower. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| cascade_trigger | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HerdingInformation.LLM.prompts:LLM_CASCADE_FOLLOWER_SYS', 'user_message': 'examples.HerdingInformation.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.HerdingInformation.RuleLLM.prompts:RULELLM_CASCADE_FOLLOWER_SYS', 'user_message': 'examples.HerdingInformation.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.HerdingInformation.Rag.prompts:RAGLLM_CASCADE_FOLLOWER_SYS', 'user_message': 'examples.HerdingInformation.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| social_weight | Rule: `0.8`<br>LLM: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | cascadefollower | CascadeFollower | `CascadeFollower` | 3 | `examples/HerdingInformation/Rule/players.py` |
| LLM | cascadefollower | CascadeFollower | `LLMCascadeFollower` | 3 | `examples/HerdingInformation/LLM/players.py` |
| RuleLLM | cascadefollower | CascadeFollower | `RuleLLMCascadeFollower` | 3 | `examples/HerdingInformation/RuleLLM/players.py` |
| Rag | cascadefollower | CascadeFollower | `RagLLMCascadeFollower` | 3 | `examples/HerdingInformation/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 CascadeFollower

**Summary**: Implements Bikhchandani et al. (1992) information cascade model. Ignores private signal once cascade_count reaches cascade_trigger threshold. Primary cascade amplifier -- follows deviation direction unconditionally after lock-in.

**Foundation**: Bikhchandani, Hirshleifer & Welch (1992); Banerjee (1992). `doi:10.1086/261849`

**Design Purpose**: Encode the rational-but-informationally-inefficient cascade: once enough consecutive observations confirm a direction (cascade_trigger rounds of |deviation| > 0.03), the agent follows the crowd regardless of its private signal.

**Behavioral Framework**:

| Decision Variable       | Logic                                              | Formula                            |
|-------------------------|----------------------------------------------------|------------------------------------|
| Cascade count increment | Each round                                         | deviation                          |
| Cascade activation      | Permanent after threshold                          | `cascade_count >= cascade_trigger`  |
| Trade size              | Proportional to deviation x social amplification   | `min(800, int(abs(dev) x social_weight x 5000))` |
| Direction               | Follow deviation (buy if dev > 0; sell if dev < 0) | Unconditional after cascade active |
| Pre-cascade             | Hold                                               | `cascade_count < cascade_trigger`  |

**Decision Walkthrough** (one round):
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. If `|deviation| > 0.03`: `cascade_count += 1`
3. If `cascade_count >= cascade_trigger`: cascade is active
4. If cascade active: `qty = min(800, int(|dev| x social_weight x 5000))`; direction = sign(deviation)
5. If cascade inactive: hold

**Worked Example** (cascade_trigger=0.3, social_weight=0.8, deviation=+0.06, cascade_count=1):
- cascade_count(1) >= cascade_trigger(0.3) -> cascade active under the current low-trigger calibration
- qty = min(800, int(0.06 x 0.8 x 5000)) = min(800, 240) = 240
- Action: buy 240 shares -- cascade lock-in

**References**: simulation-bases.md Section 2 Theory 1; `doi:10.1086/261849`

---

## Source Docstring Excerpts

### Rule / `CascadeFollower`

```text
Theory: simulation-bases.md Section 4.1 -- CascadeFollower

Theoretical basis: Information cascade theory (Bikhchandani et al., 1992).
Information cascade follower: ignores private signal, follows observed actions.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMCascadeFollower`

```text
LLM-driven information cascade follower. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMCascadeFollower`

```text
RuleLLM-driven information cascade follower. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMCascadeFollower`

```text
RagLLM-driven information cascade follower. Theory: simulation-bases.md Section 4.1.
```
