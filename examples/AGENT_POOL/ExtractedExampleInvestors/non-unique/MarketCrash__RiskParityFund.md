# MarketCrash / Risk Parity Fund

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MarketCrash |
| Agent type | Risk Parity Fund |
| Canonical class | `RiskParityFund` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A volatility-targeting institutional investor. **Theoretical and Empirical Basis**: Volatility-managed portfolios reduce risky exposure when volatility rises; see Moreira and Muir (2017, DOI: 10.1111/jofi.12575). **Design Purpose**: Add mechanical procyclical selling after volatility spikes. **Behavioral Framework**: Uses target volatility, recent volatility, rebalance speed, and base position to scale exposure. **Decision Process**: Estimate realized volatility; if volatility exceeds the target, reduce exposure; if volatility is calm, rebalance gradually. **Worked Numerical Example**: With target volatility 2.0, observed volatility 4.0, base position 50, and rebalance speed 0.3, desired exposure is roughly 25, so a current position of 50 produces a sell order near 7.5 shares. **Academic References**: Moreira and Muir (2017); Barroso and Santa-Clara (2015).

## Financial Theory / Theoretical Basis

### Rule / `RiskParityFund`
- Theory: simulation-bases.md Section 4.1.

### LLM / `LLMRiskParityFund`
- LLM RiskParityFund. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMRiskParityFund`
- Hybrid RiskParityFund. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMRiskParityFund`
- RAG RiskParityFund. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position | Rule: `50.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `50.0`<br>LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MarketCrash.LLM.prompts:LLM_RISK_PARITY_SYS', 'user_message': 'examples.MarketCrash.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_RISK_PARITY_FUND_SYS', 'user_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_RISK_PARITY_FUND_SYS', 'user_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| rebalance_speed | Rule: `0.3` | Rule |
| target_volatility | Rule: `2.0` | Rule |
| vol_lookback | Rule: `5` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | risk_parity_fund | Risk Parity Fund | `RiskParityFund` | 2 | `examples/MarketCrash/Rule/players.py` |
| LLM | llm_risk_parity | LLM Risk Parity Fund | `LLMRiskParityFund` | 2 | `examples/MarketCrash/LLM/players.py` |
| RuleLLM | rulellm_risk_parity | RuleLLM Risk Parity Fund | `RuleLLMRiskParityFund` | 2 | `examples/MarketCrash/RuleLLM/players.py` |
| Rag | ragllm_risk_parity | RAG Risk Parity Fund | `RagLLMRiskParityFund` | 2 | `examples/MarketCrash/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 RiskParityFund

**Summary**: A volatility-targeting institutional investor.
**Theoretical and Empirical Basis**: Volatility-managed portfolios reduce risky
exposure when volatility rises; see Moreira and Muir (2017, DOI:
10.1111/jofi.12575).
**Design Purpose**: Add mechanical procyclical selling after volatility spikes.
**Behavioral Framework**: Uses target volatility, recent volatility, rebalance
speed, and base position to scale exposure.
**Decision Process**: Estimate realized volatility; if volatility exceeds the
target, reduce exposure; if volatility is calm, rebalance gradually.
**Worked Numerical Example**: With target volatility 2.0, observed volatility
4.0, base position 50, and rebalance speed 0.3, desired exposure is roughly
25, so a current position of 50 produces a sell order near 7.5 shares.
**Academic References**: Moreira and Muir (2017); Barroso and Santa-Clara
(2015).

## Source Docstring Excerpts

### Rule / `RiskParityFund`

```text
Risk parity fund with volatility targeting strategy.

Theory: simulation-bases.md Section 4.1.

Parameters from config extras:
    - target_volatility, vol_lookback, rebalance_speed, base_position
```

### LLM / `LLMRiskParityFund`

```text
LLM RiskParityFund. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMRiskParityFund`

```text
Hybrid RiskParityFund. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMRiskParityFund`

```text
RAG RiskParityFund. Theory: simulation-bases.md Section 4.1.
```
