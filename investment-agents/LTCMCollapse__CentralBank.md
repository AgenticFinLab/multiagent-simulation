# LTCMCollapse / Central Bank

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LTCMCollapse |
| Agent type | Central Bank |
| Canonical class | `CentralBank` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `CentralBank` represents official-sector or coordinated private-sector lender-of-last-resort intervention. It is not a literal central-bank asset purchase model; it abstracts the 1998 coordination role into a stabilizing liquidity injection.

## Financial Theory / Theoretical Basis

### Rule / `CentralBank`
- Theory: simulation-bases.md Section 4.5 -- CentralBank
- Theoretical basis: Bagehot (1873) lender of last resort.

### LLM / `LLMCentralBank`
- Theory: simulation-bases.md Section 4.5 -- CentralBank.

### RuleLLM / `RuleLLMCentralBank`
- Theory: simulation-bases.md Section 4.5 -- CentralBank.

### Rag / `RagLLMCentralBank`
- RAG lender-of-last-resort intervention agent. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `200`<br>LLM: `200`<br>RuleLLM: `200`<br>Rag: `200` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| intervention_threshold | Rule: `0.1` | Rule |
| llm | LLM: `{'sys_message': 'examples.LTCMCollapse.LLM.prompts:LLM_CENTRALBANK_PROMPT', 'user_message': 'examples.LTCMCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_CENTRALBANK_PROMPT', 'user_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LTCMCollapse.Rag.prompts:RAG_CENTRALBANK_PROMPT', 'user_message': 'examples.LTCMCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| noise_size | Rule: `150`<br>LLM: `150`<br>RuleLLM: `150`<br>Rag: `150` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| rescue_probability | Rule: `0.5` | Rule |
| trade_probability | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | centralbank | CentralBank | `CentralBank` | 2 | `examples/LTCMCollapse/Rule/players.py` |
| LLM | centralbank | CentralBank | `LLMCentralBank` | 2 | `examples/LTCMCollapse/LLM/players.py` |
| RuleLLM | centralbank | CentralBank | `RuleLLMCentralBank` | 2 | `examples/LTCMCollapse/RuleLLM/players.py` |
| Rag | centralbank | CentralBank | `RagLLMCentralBank` | 2 | `examples/LTCMCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 CentralBank

#### Section 4.5.1 Summary

The `CentralBank` represents official-sector or coordinated private-sector lender-of-last-resort intervention. It is not a literal central-bank asset purchase model; it abstracts the 1998 coordination role into a stabilizing liquidity injection.

#### Section 4.5.2 Theoretical and Empirical Foundation

The design follows Bagehot's lender-of-last-resort principle (Section 2.5) and the historical New York Fed-facilitated coordination among LTCM counterparties.

#### Section 4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < -intervention_threshold` and random draw succeeds | Buy 2,000 | Stabilizing liquidity injection | Section 2.5 |
| Stress below threshold or failed probability draw | Hold | No intervention | Section 2.5 |

#### Section 4.5.4 Behavioral Framework

Trigger:

```
delta(t) < -intervention_threshold and u < rescue_probability
```

Sizing is fixed at 2,000 shares to model a discrete support operation.

#### Section 4.5.5 Decision Process Walkthrough

At deviation -12%, threshold 10%, and a successful probability draw, the agent buys 2,000 shares.

#### Section 4.5.6 Worked Numerical Example

With price 90, a 2,000-share intervention contributes 180,000 notional buy demand before market impact.

#### Section 4.5.7 Academic References

Bagehot (1873); Lowenstein (2000); Jorion (2000).

## Source Docstring Excerpts

### Rule / `CentralBank`

```text
Lender of last resort providing emergency liquidity during crisis.

Theory: simulation-bases.md Section 4.5 -- CentralBank
Theoretical basis: Bagehot (1873) lender of last resort.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMCentralBank`

```text
LLM-driven lender-of-last-resort intervention agent.

Theory: simulation-bases.md Section 4.5 -- CentralBank.
```

### RuleLLM / `RuleLLMCentralBank`

```text
RuleLLM lender-of-last-resort intervention agent.

Theory: simulation-bases.md Section 4.5 -- CentralBank.
```

### Rag / `RagLLMCentralBank`

```text
RAG lender-of-last-resort intervention agent. Theory: simulation-bases.md Section 4.5.
```
