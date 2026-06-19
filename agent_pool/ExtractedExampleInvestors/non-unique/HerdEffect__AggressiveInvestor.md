# HerdEffect / Aggressive Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HerdEffect |
| Agent type | Aggressive Investor |
| Canonical class | `AggressiveInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements leveraged momentum with second-derivative (acceleration) amplification. Kappa parameter larger than lambda_price -- bids more aggressively than MomentumInvestor. Largest position cap (±80).

## Financial Theory / Theoretical Basis

### Rule / `AggressiveInvestor`
- Theory: simulation-bases.md Section 4.5 -- AggressiveInvestor
- Theoretical basis: Aggressive leveraged momentum strategy (amplified trend following).
- Formula: P = P_last x (1 + κ x r); Q = β x r x cash / P + accel_bonus x acceleration.

### LLM / `LLMAggressiveInvestor`
- LLM-powered AggressiveInvestor: leveraged momentum with acceleration bonus. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMAggressiveInvestor`
- Hybrid rule+LLM AggressiveInvestor: acceleration bonus momentum. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMAggressiveInvestor`
- RAG-augmented AggressiveInvestor: leveraged momentum with retrieved knowledge. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `calculate_bid`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| accel_bonus | Rule: `0.3` | Rule |
| beta | Rule: `0.5` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| kappa | Rule: `1.0` | Rule |
| llm | LLM: `{'sys_message': 'examples.HerdEffect.LLM.prompts:LLM_AGGRESSIVE_SYS', 'user_message': 'examples.HerdEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_AGGRESSIVE_SYS', 'user_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_AGGRESSIVE_SYS', 'user_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | investor_aggressive | Aggressive Investor | `AggressiveInvestor` | 2 | `examples/HerdEffect/Rule/players.py` |
| LLM | llm_aggressive | LLM Aggressive Investor | `LLMAggressiveInvestor` | 2 | `examples/HerdEffect/LLM/players.py` |
| RuleLLM | rulellm_aggressive | RuleLLM Aggressive Investor | `RuleLLMAggressiveInvestor` | 2 | `examples/HerdEffect/RuleLLM/players.py` |
| Rag | ragllm_aggressive | RAG Aggressive Investor | `RagLLMAggressiveInvestor` | 2 | `examples/HerdEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 AggressiveInvestor

**Summary**: Implements leveraged momentum with second-derivative (acceleration) amplification. Kappa parameter larger than lambda_price -- bids more aggressively than MomentumInvestor. Largest position cap (±80).

**Foundation**: Leveraged momentum investing; acceleration-chasing as documented in hedge fund behavior during bubble episodes.

**Design Purpose**: Extreme destabilizer -- adds second-order acceleration-based amplification on top of first-order momentum. Activates most strongly during consecutive positive-return periods. Creates the sharp price spike that characterizes emergent herd peaks.

**Behavioral Framework**:

| Decision Variable   | Logic                                     | Formula                                             |
|---------------------|-------------------------------------------|-----------------------------------------------------|
| Bid price           | More aggressive than MomentumInvestor     | `P x (1 + κ x r)` where κ > lambda                       |
| Base quantity       | Return-proportional (as MomentumInvestor) | `β x r x cash / bid_price`                          |
| Acceleration bonus  | Second-derivative amplification           | `+ accel_bonus x [(P(t)-P(t-1)) - (P(t-1)-P(t-2))]` |
| Position cap        | ±80 shares                                | Largest of all agents                               |
| History requirement | Needs 3 price points for acceleration     | Falls back to return-only if < 3                    |

**Decision Walkthrough** (one round):
1. Update price_history
2. If len(price_history) >= 3: compute acceleration = `(P[-1]-P[-2]) - (P[-2]-P[-3])`
3. `bid_price = P x (1 + kappa x r)`
4. `qty = beta x r x cash / bid_price + accel_bonus x acceleration`; clip to [-80, +80]
5. Update cash/position; send order

**Worked Example** (kappa=1.0, beta=0.5, accel_bonus=0.3, P=108, r=+0.05, acceleration=+0.8, cash=10,000):
- bid_price = 108 x (1 + 1.0 x 0.05) = 113.4
- qty_base = 0.5 x 0.05 x 10,000 / 113.4 = 2.20
- qty_accel = 0.3 x 0.8 = 0.24
- qty = 2.44 -> 2 shares
- Interpretation: Buys more aggressively than MomentumInvestor; amplifies second-derivative of price

**References**: simulation-bases.md Section 2; leveraged momentum literature; `doi:10.1111/0022-1082.00188`

---

## Source Docstring Excerpts

### Rule / `AggressiveInvestor`

```text
Theory: simulation-bases.md Section 4.5 -- AggressiveInvestor

Theoretical basis: Aggressive leveraged momentum strategy (amplified trend following).
Formula: P = P_last x (1 + κ x r); Q = β x r x cash / P + accel_bonus x acceleration.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMAggressiveInvestor`

```text
LLM-powered AggressiveInvestor: leveraged momentum with acceleration bonus. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMAggressiveInvestor`

```text
Hybrid rule+LLM AggressiveInvestor: acceleration bonus momentum. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMAggressiveInvestor`

```text
RAG-augmented AggressiveInvestor: leveraged momentum with retrieved knowledge. Theory: simulation-bases.md Section 4.5.
```
