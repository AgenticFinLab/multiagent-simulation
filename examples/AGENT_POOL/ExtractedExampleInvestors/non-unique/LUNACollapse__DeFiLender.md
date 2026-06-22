# LUNACollapse / De Fi Lender

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LUNACollapse |
| Agent type | De Fi Lender |
| Canonical class | `DeFiLender` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A lending protocol participant that liquidates collateral after a sharp price decline.

## Financial Theory / Theoretical Basis

### Rule / `DeFiLender`
- Theory: simulation-bases.md Section 4.3 -- DeFiLender
- Theoretical Basis: DeFi contagion (Werner et al., 2022)

### LLM / `LLMDeFiLender`
- LLM-driven DeFi liquidation engine. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMDeFiLender`
- RuleLLM DeFi liquidation engine. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMDeFiLender`
- RAG DeFi liquidation engine. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `800`<br>LLM: `800`<br>RuleLLM: `800`<br>Rag: `800` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| liquidation_threshold | Rule: `0.15`<br>LLM: `0.15`<br>RuleLLM: `0.15`<br>Rag: `0.15` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LUNACollapse.LLM.prompts:LLM_DEFILENDER_PROMPT', 'user_message': 'examples.LUNACollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_DEFILENDER_PROMPT', 'user_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LUNACollapse.Rag.prompts:RAG_DEFILENDER_PROMPT', 'user_message': 'examples.LUNACollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | defilender | DeFiLender | `DeFiLender` | 2 | `examples/LUNACollapse/Rule/players.py` |
| LLM | defilender | DeFiLender | `LLMDeFiLender` | 2 | `examples/LUNACollapse/LLM/players.py` |
| RuleLLM | defilender | DeFiLender | `RuleLLMDeFiLender` | 2 | `examples/LUNACollapse/RuleLLM/players.py` |
| Rag | defilender | DeFiLender | `RagLLMDeFiLender` | 2 | `examples/LUNACollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 DeFiLender

**Summary**: A lending protocol participant that liquidates collateral after a
sharp price decline.

**Theoretical and Empirical Basis**: DeFi liquidations transmit price shocks
through collateral thresholds.

**Design Purpose**: Add forced selling that is not discretionary once collateral
health deteriorates.

**Behavioral Framework**: Monitors deviation and liquidation threshold.

**Decision Process**: If `deviation < -liquidation_threshold`, sell a
protocol-defined fraction of position.

**Worked Numerical Example**: With `liquidation_threshold = 0.15` and a 20%
discount, the lender enters forced-sale mode.

**Academic References**: Werner et al. (2022); DeFi liquidation literature.

## Source Docstring Excerpts

### Rule / `DeFiLender`

```text
DeFi protocol triggering forced liquidations when collateral value falls.

Theory: simulation-bases.md Section 4.3 -- DeFiLender
Theoretical Basis: DeFi contagion (Werner et al., 2022)
Market Role: destabilizing -- liquidation cascades amplify sell pressure
```

### LLM / `LLMDeFiLender`

```text
LLM-driven DeFi liquidation engine. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMDeFiLender`

```text
RuleLLM DeFi liquidation engine. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMDeFiLender`

```text
RAG DeFi liquidation engine. Theory: simulation-bases.md Section 4.3.
```
