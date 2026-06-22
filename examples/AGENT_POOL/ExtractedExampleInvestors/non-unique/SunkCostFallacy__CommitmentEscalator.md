# SunkCostFallacy / Commitment Escalator

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SunkCostFallacy |
| Agent type | Commitment Escalator |
| Canonical class | `CommitmentEscalator` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor represents decision makers who add resources to a failing position to justify prior choices.

## Financial Theory / Theoretical Basis

### Rule / `CommitmentEscalator`
- Theory: simulation-bases.md Section 4.2 -- CommitmentEscalator
- Theoretical basis: escalation of commitment (Staw, 1976).

### LLM / `LLMCommitmentEscalator`
- LLM commitment escalator doubling down on losing positions. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMCommitmentEscalator`
- RuleLLM commitment escalator doubling down on losing positions. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMCommitmentEscalator`
- RagLLM commitment escalator doubling down on losing positions. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| escalation_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| escalation_threshold | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_COMMITMENT_ESCALATOR_SYS', 'user_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_COMMITMENT_ESCALATOR_SYS', 'user_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SunkCostFallacy.Rag.prompts:RAGLLM_COMMITMENT_ESCALATOR_SYS', 'user_message': 'examples.SunkCostFallacy.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | commitmentescalator | CommitmentEscalator | `CommitmentEscalator` | 3 | `examples/SunkCostFallacy/Rule/players.py` |
| LLM | commitmentescalator | CommitmentEscalator | `LLMCommitmentEscalator` | 3 | `examples/SunkCostFallacy/LLM/players.py` |
| RuleLLM | commitmentescalator | CommitmentEscalator | `RuleLLMCommitmentEscalator` | 3 | `examples/SunkCostFallacy/RuleLLM/players.py` |
| Rag | commitmentescalator | CommitmentEscalator | `RagLLMCommitmentEscalator` | 3 | `examples/SunkCostFallacy/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 CommitmentEscalator

#### Section 4.2.1 Summary

This investor represents decision makers who add resources to a failing
position to justify prior choices.

It is the primary destabilizing biased buyer in declining markets because it
adds demand exactly when the position is losing.

#### Section 4.2.2 Theoretical and Empirical Foundation

Staw (1976) shows escalation after negative feedback. Staw and Hoang (1995)
document resource allocation affected by prior investment salience.

#### Section 4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < -escalation_threshold` | Buy to average down | Adds demand after losses | Section 2.2 |
| `deviation > escalation_threshold` | Buy smaller amount | Reinforces prior commitment | Section 2.2 |
| Small deviation | Hold | No escalation | Section 2.2 |

#### Section 4.2.4 Behavioral Framework

The agent uses `escalation_threshold` and `escalation_size`. Negative deviation
activates larger buying than positive deviation because losses intensify the
need to justify prior commitment.

#### Section 4.2.5 Decision Process Walkthrough

At a 10% loss and a 5% threshold, it buys to average down. At a 3% move it
holds because commitment pressure is not large enough.

#### Section 4.2.6 Worked Numerical Example

```text
P=90, F=100, deviation=-0.10, threshold=0.05
Q = escalation_size * |deviation| / threshold = 400 * 2 = 800 shares
```

#### Section 4.2.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Staw (1976), https://doi.org/10.1016/0030-5073(76)90005-2 | Escalation after negative feedback. |
| 2 | Staw and Hoang (1995), https://doi.org/10.2307/2393785 | Prior-investment effects in allocation. |

## Source Docstring Excerpts

### Rule / `CommitmentEscalator`

```text
Doubles down on losing positions, increasing exposure to justify prior commitment.

Theory: simulation-bases.md Section 4.2 -- CommitmentEscalator
Theoretical basis: escalation of commitment (Staw, 1976).
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMCommitmentEscalator`

```text
LLM commitment escalator doubling down on losing positions. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMCommitmentEscalator`

```text
RuleLLM commitment escalator doubling down on losing positions. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMCommitmentEscalator`

```text
RagLLM commitment escalator doubling down on losing positions. Theory: simulation-bases.md Section 4.2.
```
