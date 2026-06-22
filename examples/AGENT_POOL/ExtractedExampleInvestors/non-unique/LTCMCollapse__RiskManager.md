# LTCMCollapse / Risk Manager

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LTCMCollapse |
| Agent type | Risk Manager |
| Canonical class | `RiskManager` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `RiskManager` represents institutional risk-control desks that cut exposure when deviations exceed allowed risk limits. The agent is stabilizing at the individual-book level but can amplify systemic stress when many agents cut positions simultaneously.

## Financial Theory / Theoretical Basis

### Rule / `RiskManager`
- Theory: simulation-bases.md Section 4.3 -- RiskManager
- Theoretical basis: Jorion (2000) VaR and LTCM risk-management lessons.

### LLM / `LLMRiskManager`
- Theory: simulation-bases.md Section 4.3 -- RiskManager.

### RuleLLM / `RuleLLMRiskManager`
- Theory: simulation-bases.md Section 4.3 -- RiskManager.

### Rag / `RagLLMRiskManager`
- RAG VaR-based position cutter. Theory: simulation-bases.md Section 4.3.

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
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LTCMCollapse.LLM.prompts:LLM_RISKMANAGER_PROMPT', 'user_message': 'examples.LTCMCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_RISKMANAGER_PROMPT', 'user_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LTCMCollapse.Rag.prompts:RAG_RISKMANAGER_PROMPT', 'user_message': 'examples.LTCMCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| var_limit | Rule: `0.05` | Rule |
| var_trigger | Rule: `0.06`<br>LLM: `0.06`<br>RuleLLM: `0.06`<br>Rag: `0.06` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | riskmanager | RiskManager | `RiskManager` | 2 | `examples/LTCMCollapse/Rule/players.py` |
| LLM | riskmanager | RiskManager | `LLMRiskManager` | 2 | `examples/LTCMCollapse/LLM/players.py` |
| RuleLLM | riskmanager | RiskManager | `RuleLLMRiskManager` | 2 | `examples/LTCMCollapse/RuleLLM/players.py` |
| Rag | riskmanager | RiskManager | `RagLLMRiskManager` | 2 | `examples/LTCMCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 RiskManager

#### Section 4.3.1 Summary

The `RiskManager` represents institutional risk-control desks that cut exposure when deviations exceed allowed risk limits. The agent is stabilizing at the individual-book level but can amplify systemic stress when many agents cut positions simultaneously.

#### Section 4.3.2 Theoretical and Empirical Foundation

The design is based on VaR procyclicality (Section 2.3). It operationalizes a risk breach when price deviation exceeds three times the configured VaR limit.

#### Section 4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) > 3 * var_limit` and long | Sell 50% of position | Risk reduction, possible sell pressure | Section 2.3 |
| `abs(deviation) > 3 * var_limit` and short | Buy to cover 50% | Risk reduction, possible buy pressure | Section 2.3 |
| Within risk limits | Hold | No action | Section 2.3 |

#### Section 4.3.4 Behavioral Framework

Trigger:

```
|delta(t)| > 3 * VaR_limit
```

Sizing:

```
Q_cut(t) = floor(0.50 * |position(t)|)
```

#### Section 4.3.5 Decision Process Walkthrough

At `var_limit = 0.05`, a 16% deviation exceeds `3 * var_limit = 15%`, causing a 50% position cut.

#### Section 4.3.6 Worked Numerical Example

If position is 500 and deviation is -0.16:

```
Q = floor(0.50 * 500) = 250 sell
```

#### Section 4.3.7 Academic References

Jorion (2000); Danielsson et al. (2001), "An academic response to Basel II."

## Source Docstring Excerpts

### Rule / `RiskManager`

```text
Monitors portfolio risk and cuts positions when VaR thresholds are breached.

Theory: simulation-bases.md Section 4.3 -- RiskManager
Theoretical basis: Jorion (2000) VaR and LTCM risk-management lessons.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMRiskManager`

```text
LLM-driven VaR-based position cutter.

Theory: simulation-bases.md Section 4.3 -- RiskManager.
```

### RuleLLM / `RuleLLMRiskManager`

```text
RuleLLM VaR-based position cutter.

Theory: simulation-bases.md Section 4.3 -- RiskManager.
```

### Rag / `RagLLMRiskManager`

```text
RAG VaR-based position cutter. Theory: simulation-bases.md Section 4.3.
```
