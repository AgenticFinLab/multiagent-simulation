# HerdEffect / Risk Averse Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HerdEffect |
| Agent type | Risk Averse Investor |
| Canonical class | `RiskAverseInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Markowitz (1952) mean-variance optimization. Target position inversely proportional to price variance. Gradually adjusts toward target at 30 %/round. Smallest position cap (±20).

## Financial Theory / Theoretical Basis

### Rule / `RiskAverseInvestor`
- Theory: simulation-bases.md Section 4.3 -- RiskAverseInvestor
- Theoretical basis: Mean-variance optimization (Markowitz, 1952).
- Formula: Q = k / sigma² x cash / P; position adjusted toward target gradually.

### LLM / `LLMRiskAverseInvestor`
- LLM-powered RiskAverseInvestor: volatility-sensitive mean-variance strategy. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMRiskAverseInvestor`
- Hybrid rule+LLM RiskAverseInvestor: managing volatility. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMRiskAverseInvestor`
- RAG-augmented RiskAverseInvestor: volatility-sensitive strategy with retrieved knowledge. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `calculate_bid`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| k | Rule: `0.5` | Rule |
| llm | LLM: `{'sys_message': 'examples.HerdEffect.LLM.prompts:LLM_RISK_AVERSE_SYS', 'user_message': 'examples.HerdEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_RISK_AVERSE_SYS', 'user_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_RISK_AVERSE_SYS', 'user_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback | Rule: `5` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | investor_risk_averse | Risk Averse Investor | `RiskAverseInvestor` | 2 | `examples/HerdEffect/Rule/players.py` |
| LLM | llm_risk_averse | LLM Risk Averse Investor | `LLMRiskAverseInvestor` | 2 | `examples/HerdEffect/LLM/players.py` |
| RuleLLM | rulellm_risk_averse | RuleLLM Risk Averse Investor | `RuleLLMRiskAverseInvestor` | 2 | `examples/HerdEffect/RuleLLM/players.py` |
| Rag | ragllm_risk_averse | RAG Risk Averse Investor | `RagLLMRiskAverseInvestor` | 2 | `examples/HerdEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 RiskAverseInvestor

**Summary**: Implements Markowitz (1952) mean-variance optimization. Target position inversely proportional to price variance. Gradually adjusts toward target at 30 %/round. Smallest position cap (±20).

**Foundation**: Markowitz (1952) mean-variance; Tobin (1958) risk-return tradeoff. `doi:10.1111/j.1540-6261.1952.tb01525.x`

**Design Purpose**: Create early-exit selling signal when momentum builds volatility. Paradoxically accelerates herd by reducing stabilizing supply -- the "volatility exit" that removes a dampening force at peak momentum.

**Behavioral Framework**:

| Decision Variable | Logic                              | Formula                          |
|-------------------|------------------------------------|----------------------------------|
| Price variance    | Rolling window                     | `Var(P[t-lookback:t])`           |
| Target quantity   | Inversely proportional to variance | `k / variance x cash / P`        |
| Actual trade      | Gradual adjustment                 | `(target_qty - position) x 0.30` |
| Position cap      | ±20 shares                         | Smallest of all agents           |

**Decision Walkthrough** (one round):
1. Update price_history with new price
2. Compute `variance = Var(price_history[-lookback:])`
3. `target_qty = k / variance x cash / P`
4. `qty = (target_qty - position) x 0.30`; clip to [-20, +20]
5. Update cash/position; send order

**Worked Example** (k=0.5, lookback=5, position=10, P=110, variance=4.0, cash=10,000):
- target_qty = 0.5 / 4.0 x 10,000 / 110 = 11.36
- (target_qty=11.36 - position=10) x 0.30 = 0.41 -> hold / small buy after integer rounding
- Interpretation: Variance is moderate; the investor remains near target exposure and sells as variance rises

**References**: simulation-bases.md Section 2 Theory 3; `doi:10.1111/j.1540-6261.1952.tb01525.x`

---

## Source Docstring Excerpts

### Rule / `RiskAverseInvestor`

```text
Theory: simulation-bases.md Section 4.3 -- RiskAverseInvestor

Theoretical basis: Mean-variance optimization (Markowitz, 1952).
Formula: Q = k / sigma² x cash / P; position adjusted toward target gradually.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMRiskAverseInvestor`

```text
LLM-powered RiskAverseInvestor: volatility-sensitive mean-variance strategy. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMRiskAverseInvestor`

```text
Hybrid rule+LLM RiskAverseInvestor: managing volatility. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMRiskAverseInvestor`

```text
RAG-augmented RiskAverseInvestor: volatility-sensitive strategy with retrieved knowledge. Theory: simulation-bases.md Section 4.3.
```
