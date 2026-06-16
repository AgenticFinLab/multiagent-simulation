# StatusQuoBias / Active Rebalancer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | StatusQuoBias |
| Agent type | Active Rebalancer |
| Canonical class | `ActiveRebalancer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor represents portfolio managers who respond directly to valuation gaps and rebalance toward fundamental value.

## Financial Theory / Theoretical Basis

### Rule / `ActiveRebalancer`
- Theory: simulation-bases.md Section 4.3 -- ActiveRebalancer
- Theoretical basis: rational portfolio rebalancing benchmark.

### LLM / `LLMActiveRebalancer`
- LLM-driven active rebalancer adjusting on new information. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMActiveRebalancer`
- RuleLLM active rebalancer adjusting on new information. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMActiveRebalancer`
- RagLLM active rebalancer adjusting on new information. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.StatusQuoBias.LLM.prompts:LLM_ACTIVE_REBALANCER_SYS', 'user_message': 'examples.StatusQuoBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_ACTIVE_REBALANCER_SYS', 'user_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.StatusQuoBias.Rag.prompts:RAGLLM_ACTIVE_REBALANCER_SYS', 'user_message': 'examples.StatusQuoBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| rebalance_threshold | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | activerebalancer | ActiveRebalancer | `ActiveRebalancer` | 2 | `examples/StatusQuoBias/Rule/players.py` |
| LLM | activerebalancer | ActiveRebalancer | `LLMActiveRebalancer` | 2 | `examples/StatusQuoBias/LLM/players.py` |
| RuleLLM | activerebalancer | ActiveRebalancer | `RuleLLMActiveRebalancer` | 2 | `examples/StatusQuoBias/RuleLLM/players.py` |
| Rag | activerebalancer | ActiveRebalancer | `RagLLMActiveRebalancer` | 2 | `examples/StatusQuoBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 ActiveRebalancer

#### Section 4.3.1 Summary

This investor represents portfolio managers who respond directly to valuation
gaps and rebalance toward fundamental value.

It is the rational benchmark against which inertial and default-following agents
are compared.

#### Section 4.3.2 Theoretical and Empirical Foundation

Markowitz (1952) motivates active portfolio adjustment. Standard rebalancing
practice motivates trading after valuation drift exceeds a threshold.

#### Section 4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < -rebalance_threshold` | Buy | Speeds undervaluation correction | Section 2.4 |
| `deviation > rebalance_threshold` | Sell | Speeds overvaluation correction | Section 2.4 |
| Small deviation | Hold | Avoids noise trading | Section 2.4 |

#### Section 4.3.4 Behavioral Framework

The agent uses `rebalance_threshold` and `position_size`. Quantity increases
with absolute deviation and is bounded by cash or inventory.

#### Section 4.3.5 Decision Process Walkthrough

If price is 94, fundamental is 100, and threshold is 5%, the agent buys because
the asset is undervalued by 6%.

#### Section 4.3.6 Worked Numerical Example

```text
P=94, F=100, delta=-0.06, threshold=0.05
Q = 350 * 0.06 / 0.05 = 420 shares
```

#### Section 4.3.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Markowitz (1952), https://doi.org/10.1111/j.1540-6261.1952.tb01525.x | Rational portfolio response benchmark. |
| 2 | Benartzi and Thaler (2007), https://doi.org/10.1257/jep.21.3.81 | Contrast between active choice and inertia. |

## Source Docstring Excerpts

### Rule / `ActiveRebalancer`

```text
Proactively adjusts positions based on new information regardless of current holdings.

Theory: simulation-bases.md Section 4.3 -- ActiveRebalancer
Theoretical basis: rational portfolio rebalancing benchmark.
See simulation-bases.md Section 4.3 for mathematical model.

Parameters from config extras:
    - rebalance_threshold, position_size
```

### LLM / `LLMActiveRebalancer`

```text
LLM-driven active rebalancer adjusting on new information. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMActiveRebalancer`

```text
RuleLLM active rebalancer adjusting on new information. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMActiveRebalancer`

```text
RagLLM active rebalancer adjusting on new information. Theory: simulation-bases.md Section 4.3.
```
