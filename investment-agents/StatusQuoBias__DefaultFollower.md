# StatusQuoBias / Default Follower

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | StatusQuoBias |
| Agent type | Default Follower |
| Canonical class | `DefaultFollower` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor represents retirement-plan participants and passive allocators who accept a default portfolio unless drift is highly visible.

## Financial Theory / Theoretical Basis

### Rule / `DefaultFollower`
- Theory: simulation-bases.md Section 4.2 -- DefaultFollower
- Theoretical basis: default bias and decision avoidance.

### LLM / `LLMDefaultFollower`
- LLM-driven default follower avoiding active decisions. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMDefaultFollower`
- RuleLLM default follower avoiding active decisions. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMDefaultFollower`
- RagLLM default follower avoiding active decisions. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| active_deviation | Rule: `0.15`<br>LLM: `0.15`<br>RuleLLM: `0.15`<br>Rag: `0.15` | LLM, Rag, Rule, RuleLLM |
| base_size | Rule: `250`<br>LLM: `250`<br>RuleLLM: `250`<br>Rag: `250` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| default_weight | Rule: `0.5`<br>LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.StatusQuoBias.LLM.prompts:LLM_DEFAULT_FOLLOWER_SYS', 'user_message': 'examples.StatusQuoBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_DEFAULT_FOLLOWER_SYS', 'user_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.StatusQuoBias.Rag.prompts:RAGLLM_DEFAULT_FOLLOWER_SYS', 'user_message': 'examples.StatusQuoBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | defaultfollower | DefaultFollower | `DefaultFollower` | 3 | `examples/StatusQuoBias/Rule/players.py` |
| LLM | defaultfollower | DefaultFollower | `LLMDefaultFollower` | 3 | `examples/StatusQuoBias/LLM/players.py` |
| RuleLLM | defaultfollower | DefaultFollower | `RuleLLMDefaultFollower` | 3 | `examples/StatusQuoBias/RuleLLM/players.py` |
| Rag | defaultfollower | DefaultFollower | `RagLLMDefaultFollower` | 3 | `examples/StatusQuoBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 DefaultFollower

#### Section 4.2.1 Summary

This investor represents retirement-plan participants and passive allocators who
accept a default portfolio unless drift is highly visible.

In the simulation it creates allocation persistence that is distinct from pure
status quo bias because the reference point is an externally supplied default.

#### Section 4.2.2 Theoretical and Empirical Foundation

Madrian and Shea (2001) document automatic-enrollment effects. Cronqvist and
Thaler (2004) show persistent default choices in pension allocation.

#### Section 4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `abs(deviation) <= active_deviation` | Hold | Maintains default allocation | Section 2.2 |
| `deviation < -active_deviation` | Buy | Rebalances only after large undervaluation | Section 2.2 |
| `deviation > active_deviation` | Sell | Trims only after large overvaluation | Section 2.2 |

#### Section 4.2.4 Behavioral Framework

The agent uses `active_deviation`, `default_weight`, and `base_size`. It treats
the default allocation as acceptable unless the valuation gap is large.

#### Section 4.2.5 Decision Process Walkthrough

At a 10% deviation and `active_deviation=0.15`, the agent holds. At a 20%
deviation, it submits a trade scaled by default weight.

#### Section 4.2.6 Worked Numerical Example

```text
P=80, F=100, delta=-0.20, active_deviation=0.15
Q = base_size * |delta| / active_deviation * default_weight
Q = 250 * 1.333 * 0.5 = 166 shares
```

#### Section 4.2.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Madrian and Shea (2001), https://doi.org/10.1162/003355301753265543 | Default-induced allocation persistence. |
| 2 | Cronqvist and Thaler (2004), https://doi.org/10.1257/0002828041301633 | Pension default portfolio persistence. |

## Source Docstring Excerpts

### Rule / `DefaultFollower`

```text
Follows default allocation suggestions, avoids active decisions.

Theory: simulation-bases.md Section 4.2 -- DefaultFollower
Theoretical basis: default bias and decision avoidance.
See simulation-bases.md Section 4.2 for mathematical model.

Parameters from config extras:
    - default_weight, active_deviation
```

### LLM / `LLMDefaultFollower`

```text
LLM-driven default follower avoiding active decisions. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMDefaultFollower`

```text
RuleLLM default follower avoiding active decisions. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMDefaultFollower`

```text
RagLLM default follower avoiding active decisions. Theory: simulation-bases.md Section 4.2.
```
