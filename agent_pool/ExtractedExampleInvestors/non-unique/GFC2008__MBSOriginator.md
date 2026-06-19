# GFC2008 / MBS Originator

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GFC2008 |
| Agent type | MBS Originator |
| Canonical class | `MBSOriginator` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`MBSOriginator` represents the originate-to-distribute pipeline that steadily sells securitized mortgage exposure. It supplies the market with risky securities even when prices weaken, reflecting fee-income incentives rather than long-horizon asset performance.

## Financial Theory / Theoretical Basis

### Rule / `MBSOriginator`
- Theory: simulation-bases.md Section 4.1 -- MBSOriginator
- Theoretical basis: Originate-to-distribute model (Keys et al., 2010).

### LLM / `LLMMBSOriginator`
- LLM-driven MBSOriginator: creates structured securities with lax screening. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMMBSOriginator`
- RuleLLM-driven MBSOriginator: creates structured securities with lax screening. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMMBSOriginator`
- RAG-augmented MBSOriginator: creates structured securities with lax screening. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `3000`<br>LLM: `3000`<br>RuleLLM: `3000`<br>Rag: `3000` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GFC2008.LLM.prompts:LLM_MBS_ORIGINATOR_SYS', 'user_message': 'examples.GFC2008.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_MBS_ORIGINATOR_SYS', 'user_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GFC2008.Rag.prompts:RAGLLM_MBS_ORIGINATOR_SYS', 'user_message': 'examples.GFC2008.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| origination_rate | Rule: `0.08`<br>LLM: `0.08`<br>RuleLLM: `0.08`<br>Rag: `0.08` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | mbsoriginator | MBSOriginator | `MBSOriginator` | 2 | `examples/GFC2008/Rule/players.py` |
| LLM | mbsoriginator | MBSOriginator | `LLMMBSOriginator` | 2 | `examples/GFC2008/LLM/players.py` |
| RuleLLM | mbsoriginator | MBSOriginator | `RuleLLMMBSOriginator` | 2 | `examples/GFC2008/RuleLLM/players.py` |
| Rag | mbsoriginator | MBSOriginator | `RagLLMMBSOriginator` | 2 | `examples/GFC2008/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 MBSOriginator

#### Section 4.1.1 Summary

`MBSOriginator` represents the originate-to-distribute pipeline that steadily sells securitized mortgage exposure. It supplies the market with risky securities even when prices weaken, reflecting fee-income incentives rather than long-horizon asset performance.

#### Section 4.1.2 Theoretical and Empirical Foundation

The agent is grounded in Keys et al. (2010) on securitization and lax screening, and in Gorton (2010) on securitized banking fragility. The agent's supply behavior creates the raw inventory that rating-driven demand and leveraged holdings absorb.

#### Section 4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| every round with positive inventory | sell `int(position * origination_rate)` | persistent MBS supply | Section 2 Theory 1 |
| inventory depleted | hold | distribution channel exhausted | Section 2 Theory 1 |

#### Section 4.1.4 Behavioral Framework

```
sell_qty = int(position * origination_rate)
if position > 0 and sell_qty > 0: sell
else: hold
```

#### Section 4.1.5 Decision Process Walkthrough

With 3,000 securities and `origination_rate = 0.08`, the originator sells 240 securities in the first round regardless of price. The quantity shrinks as inventory is distributed.

#### Section 4.1.6 Worked Numerical Example

At price 100, selling 240 units raises 24,000 in cash and reduces inventory to 2,760.

#### Section 4.1.7 Academic References

Keys et al. (2010); Gorton (2010).

## Source Docstring Excerpts

### Rule / `MBSOriginator`

```text
Theory: simulation-bases.md Section 4.1 -- MBSOriginator

Theoretical basis: Originate-to-distribute model (Keys et al., 2010).
Creates mortgage-backed securities with lax screening; originate-to-distribute model.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMMBSOriginator`

```text
LLM-driven MBSOriginator: creates structured securities with lax screening. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMMBSOriginator`

```text
RuleLLM-driven MBSOriginator: creates structured securities with lax screening. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMMBSOriginator`

```text
RAG-augmented MBSOriginator: creates structured securities with lax screening. Theory: simulation-bases.md Section 4.1.
```
