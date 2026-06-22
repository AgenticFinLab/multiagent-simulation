# DotComBubble / Momentum Follower

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DotComBubble |
| Agent type | Momentum Follower |
| Canonical class | `MomentumFollower` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

Trend-following investor that buys recent winners and sells recent losers. It amplifies both the run-up and the crash.

## Financial Theory / Theoretical Basis

### Rule / `MomentumFollower`
- Follows price trends and amplifies moves -- trend-chasing behavior.
- Theory: simulation-bases.md Section 4.3 -- MomentumFollower
- Theoretical basis: Abreu & Brunnermeier (2003) momentum synchronization; Jegadeesh & Titman (1993).

### LLM / `LLMMomentumFollower`
- LLM-driven momentum follower -- amplifies trends, rides bubble. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMMomentumFollower`
- RuleLLM-driven momentum follower -- momentum threshold rules embedded. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMMomentumFollower`
- RAG-augmented momentum follower -- trend amplifier with historical momentum research. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| entry_threshold | Rule: `0.03`<br>LLM: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DotComBubble.LLM.prompts:LLM_MOMENTUM_FOLLOWER_SYS', 'user_message': 'examples.DotComBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_MOMENTUM_FOLLOWER_SYS', 'user_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.DotComBubble.Rag.prompts:RAG_MOMENTUM_FOLLOWER_SYS', 'user_message': 'examples.DotComBubble.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| momentum_threshold | Rule: `0.02` | Rule |
| order_size | Rule: `500` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentumfollower | MomentumFollower | `MomentumFollower` | 2 | `examples/DotComBubble/Rule/players.py` |
| LLM | momentumfollower | MomentumFollower | `LLMMomentumFollower` | 2 | `examples/DotComBubble/LLM/players.py` |
| RuleLLM | momentumfollower | MomentumFollower | `RuleLLMMomentumFollower` | 2 | `examples/DotComBubble/RuleLLM/players.py` |
| Rag | momentumfollower | MomentumFollower | `RagLLMMomentumFollower` | 2 | `examples/DotComBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 MomentumFollower

#### Section 4.3.1 Summary

Trend-following investor that buys recent winners and sells recent losers. It amplifies both the run-up and the crash.

#### Section 4.3.2 Theoretical and Empirical Foundation

The basis is price momentum (Section 2.3). In a bubble, trend following can turn narrative demand into mechanically amplified demand.

#### Section 4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `momentum > momentum_threshold` | buy | amplifies price rise | Section 2.3 |
| `momentum < -momentum_threshold` | sell | accelerates crash | Section 2.3 |

#### Section 4.3.4 Behavioral Framework

```
momentum = (P(t) - P(t-1)) / P(t-1)
if momentum > threshold: buy min(order_size, cash / price)
elif momentum < -threshold: sell min(order_size, position)
else: hold
```

#### Section 4.3.5 Decision Process Walkthrough

If price rises from 100 to 103, momentum is 3%. With threshold 2%, the agent buys.

#### Section 4.3.6 Worked Numerical Example

With cash 60,000, price 103, and `order_size = 500`, buy quantity is `min(500, floor(60000/103)) = 500`.

#### Section 4.3.7 Academic References

Jegadeesh & Titman (1993); Abreu & Brunnermeier (2003).

## Source Docstring Excerpts

### Rule / `MomentumFollower`

```text
Follows price trends and amplifies moves -- trend-chasing behavior.

Theory: simulation-bases.md Section 4.3 -- MomentumFollower
Theoretical basis: Abreu & Brunnermeier (2003) momentum synchronization; Jegadeesh & Titman (1993).
See simulation-bases.md Section 4.3 for mathematical model.
Role: destabilizing.
```

### LLM / `LLMMomentumFollower`

```text
LLM-driven momentum follower -- amplifies trends, rides bubble. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMMomentumFollower`

```text
RuleLLM-driven momentum follower -- momentum threshold rules embedded. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMMomentumFollower`

```text
RAG-augmented momentum follower -- trend amplifier with historical momentum research. Theory: simulation-bases.md Section 4.3.
```
