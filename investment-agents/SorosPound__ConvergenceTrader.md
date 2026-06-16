# SorosPound / Convergence Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SorosPound |
| Agent type | Convergence Trader |
| Canonical class | `ConvergenceTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A trader that expects the peg relationship to remain viable and adds intermittent stabilizing or destabilizing flow.

## Financial Theory / Theoretical Basis

### Rule / `ConvergenceTrader`
- Theory: simulation-bases.md Section 4.3

### LLM / `LLMConvergenceTrader`
- Theory: simulation-bases.md Section 4.3

### RuleLLM / `RuleLLMConvergenceTrader`
- Theory: simulation-bases.md Section 4.3

### Rag / `RagLLMConvergenceTrader`
- Theory: simulation-bases.md Section 4.3

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| convergence_threshold | Rule: `0.03`<br>LLM: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `95.0`<br>LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SorosPound.LLM.prompts:LLM_CONVERGENCE_TRADER_SYS', 'user_message': 'examples.SorosPound.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_CONVERGENCE_TRADER_SYS', 'user_message': 'examples.SorosPound.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SorosPound.Rag.prompts:RAGLLM_CONVERGENCE_TRADER_SYS', 'user_message': 'examples.SorosPound.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | convergencetrader | ConvergenceTrader | `ConvergenceTrader` | 2 | `examples/SorosPound/Rule/players.py` |
| LLM | convergencetrader | ConvergenceTrader | `LLMConvergenceTrader` | 2 | `examples/SorosPound/LLM/players.py` |
| RuleLLM | convergencetrader | ConvergenceTrader | `RuleLLMConvergenceTrader` | 2 | `examples/SorosPound/RuleLLM/players.py` |
| Rag | convergencetrader | ConvergenceTrader | `RagLLMConvergenceTrader` | 2 | `examples/SorosPound/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 ConvergenceTrader

**Summary**: A trader that expects the peg relationship to remain viable and
adds intermittent stabilizing or destabilizing flow.

**Theoretical and Empirical Basis**: Convergence strategies rely on policy
commitment, but their risk rises sharply when a peg's credibility weakens.

**Design Purpose**: Add capital that is not purely informed attack pressure and
can be wrong-footed by a peg break.

**Behavioral Framework**: The retained Rule implementation trades randomly in
30% of rounds with random direction and quantity between 100 and 500, constrained
by cash and inventory.

**Decision Process**: Decide whether to trade using the stochastic 30% rule;
then choose buy or sell randomly and apply portfolio constraints.

**Worked Numerical Example**: If the random trade gate opens and the sampled
quantity is 350, a buy order is capped by `floor(cash / price)` and a sell order
by current position.

**Academic References**: Currency convergence and policy-risk mechanisms in
European Monetary System crisis studies.

## Source Docstring Excerpts

### Rule / `ConvergenceTrader`

```text
Convergence trader.

Theory: simulation-bases.md Section 4.3
```

### LLM / `LLMConvergenceTrader`

```text
LLM-driven convergence trader.

Theory: simulation-bases.md Section 4.3
```

### RuleLLM / `RuleLLMConvergenceTrader`

```text
RuleLLM convergence trader.

Theory: simulation-bases.md Section 4.3
```

### Rag / `RagLLMConvergenceTrader`

```text
RAG-augmented convergence trader.

Theory: simulation-bases.md Section 4.3
```
