# SunkCostFallacy / Sunk Cost Holder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SunkCostFallacy |
| Agent type | Sunk Cost Holder |
| Canonical class | `SunkCostHolder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor represents traders who keep a losing position because exiting would make the prior mistake explicit.

## Financial Theory / Theoretical Basis

### Rule / `SunkCostHolder`
- Theory: simulation-bases.md Section 4.1 -- SunkCostHolder
- Theoretical basis: sunk cost escalation (Arkes & Blumer, 1985).

### LLM / `LLMSunkCostHolder`
- LLM sunk cost holder refusing to cut losing positions. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMSunkCostHolder`
- RuleLLM sunk cost holder refusing to cut losing positions. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMSunkCostHolder`
- RagLLM sunk cost holder refusing to cut losing positions. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `200`<br>LLM: `200`<br>RuleLLM: `200`<br>Rag: `200` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| hold_threshold | Rule: `0.1`<br>LLM: `0.1`<br>RuleLLM: `0.1`<br>Rag: `0.1` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_SUNK_COST_HOLDER_SYS', 'user_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_SUNK_COST_HOLDER_SYS', 'user_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SunkCostFallacy.Rag.prompts:RAGLLM_SUNK_COST_HOLDER_SYS', 'user_message': 'examples.SunkCostFallacy.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | sunkcostholder | SunkCostHolder | `SunkCostHolder` | 3 | `examples/SunkCostFallacy/Rule/players.py` |
| LLM | sunkcostholder | SunkCostHolder | `LLMSunkCostHolder` | 3 | `examples/SunkCostFallacy/LLM/players.py` |
| RuleLLM | sunkcostholder | SunkCostHolder | `RuleLLMSunkCostHolder` | 3 | `examples/SunkCostFallacy/RuleLLM/players.py` |
| Rag | sunkcostholder | SunkCostHolder | `RagLLMSunkCostHolder` | 3 | `examples/SunkCostFallacy/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 SunkCostHolder

#### Section 4.1.1 Summary

This investor represents traders who keep a losing position because exiting
would make the prior mistake explicit.

Its simulation role is to create sticky supply: it withholds sell pressure after
losses and can continue buying when prior commitment appears vindicated.

#### Section 4.1.2 Theoretical and Empirical Foundation

Arkes and Blumer (1985) establish the sunk-cost fallacy experimentally. Odean
(1998) documents reluctance to realize losses in brokerage accounts.

#### Section 4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < 0` | Hold | Refuses to realize loss | Section 2.1 |
| `deviation > hold_threshold` | Buy modestly | Prior commitment is reinforced | Section 2.3 |
| Small deviation | Hold | No active reallocation | Section 2.1 |

#### Section 4.1.4 Behavioral Framework

The agent observes price, fundamental, and deviation. It does not sell losing
positions. It may buy when positive performance makes prior commitment feel
validated.

#### Section 4.1.5 Decision Process Walkthrough

At price 90 and fundamental 100, the agent holds rather than selling. At price
112 and `hold_threshold=0.10`, it may buy a small amount.

#### Section 4.1.6 Worked Numerical Example

```text
P=112, F=100, deviation=0.12, hold_threshold=0.10
Q = base_size * deviation / hold_threshold = 200 * 1.2 = 240 shares
```

#### Section 4.1.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Arkes and Blumer (1985), https://doi.org/10.1016/0749-5978(85)90049-4 | Sunk-cost mechanism. |
| 2 | Odean (1998), https://doi.org/10.1111/0022-1082.00072 | Refusal to realize losses. |

## Source Docstring Excerpts

### Rule / `SunkCostHolder`

```text
Holds losing positions because of prior investment, refuses to cut losses.

Theory: simulation-bases.md Section 4.1 -- SunkCostHolder
Theoretical basis: sunk cost escalation (Arkes & Blumer, 1985).
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMSunkCostHolder`

```text
LLM sunk cost holder refusing to cut losing positions. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMSunkCostHolder`

```text
RuleLLM sunk cost holder refusing to cut losing positions. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMSunkCostHolder`

```text
RagLLM sunk cost holder refusing to cut losing positions. Theory: simulation-bases.md Section 4.1.
```
