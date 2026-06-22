# HerdEffect / Momentum Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HerdEffect |
| Agent type | Momentum Investor |
| Canonical class | `MomentumInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Shiller (1984) positive feedback trading -- buys when price rises, sells when price falls. Primary emergent herding amplifier. Bid price is return-scaled above current price.

## Financial Theory / Theoretical Basis

### Rule / `MomentumInvestor`
- Theory: simulation-bases.md Section 4.1 -- MomentumInvestor
- Theoretical basis: Momentum strategy / trend following (Jegadeesh & Titman, 1993).
- Formula: P = P_last x (1 + lambda x r); Q = β x r x cash / P.

### LLM / `LLMMomentumInvestor`
- LLM-powered MomentumInvestor: trend following strategy. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMMomentumInvestor`
- Hybrid rule+LLM MomentumInvestor: following trend signals. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMMomentumInvestor`
- RAG-augmented MomentumInvestor: trend following with retrieved knowledge. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `calculate_bid`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| beta | Rule: `0.3` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| lambda_price | Rule: `0.5` | Rule |
| llm | LLM: `{'sys_message': 'examples.HerdEffect.LLM.prompts:LLM_MOMENTUM_SYS', 'user_message': 'examples.HerdEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_MOMENTUM_SYS', 'user_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_MOMENTUM_SYS', 'user_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | investor_momentum | Momentum Investor | `MomentumInvestor` | 2 | `examples/HerdEffect/Rule/players.py` |
| LLM | llm_momentum | LLM Momentum Investor | `LLMMomentumInvestor` | 2 | `examples/HerdEffect/LLM/players.py` |
| RuleLLM | rulellm_momentum | RuleLLM Momentum Investor | `RuleLLMMomentumInvestor` | 3 | `examples/HerdEffect/RuleLLM/players.py` |
| Rag | ragllm_momentum | RAG Momentum Investor | `RagLLMMomentumInvestor` | 3 | `examples/HerdEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 MomentumInvestor

**Summary**: Implements Shiller (1984) positive feedback trading -- buys when price rises, sells when price falls. Primary emergent herding amplifier. Bid price is return-scaled above current price.

**Foundation**: Shiller (1984) positive feedback; Jegadeesh & Titman (1993) momentum. `doi:10.2307/2534436`; `doi:10.2307/2328882`

**Design Purpose**: Convert noise signal into sustained momentum episode; first-order return response that creates MomentumInvestor convergence when multiple agents respond to same positive return signal.

**Behavioral Framework**:

| Decision Variable | Logic                                   | Formula                    |
|-------------------|-----------------------------------------|----------------------------|
| Bid price         | Scale above market by return strength   | `P x (1 + lambda x r)`          |
| Quantity          | Proportional to return x available cash | `β x r x cash / bid_price` |
| Position cap      | ±50 shares                              | Hard limit                 |
| Hold condition    | r ≈ 0 (no strong signal)                | `quantity ≈ 0`             |

**Decision Walkthrough** (one round):
1. Receive market broadcast: `{price, return, volume, net_demand, round}`
2. Compute `r = return` (pre-computed in broadcast)
3. `bid_price = P x (1 + lambda_price x r)`
4. `qty = beta x r x cash / bid_price`; clip to [-50, +50]
5. Update cash/position in `decide()`: `cash -= bid_price x qty`; `position += qty`
6. Send order to Market via `act()`

**Worked Example** (lambda_price=0.5, beta=0.3, cash=10,000, P=105, r=+0.05):
- bid_price = 105 x (1 + 0.5 x 0.05) = 107.63
- qty = 0.3 x 0.05 x 10,000 / 107.63 = 1.39 -> 1 share
- Interpretation: Buys 1 share at 107.63; reinforces upward move

**References**: simulation-bases.md Section 2 Theory 1; `doi:10.2307/2534436`

---

## Source Docstring Excerpts

### Rule / `MomentumInvestor`

```text
Theory: simulation-bases.md Section 4.1 -- MomentumInvestor

Theoretical basis: Momentum strategy / trend following (Jegadeesh & Titman, 1993).
Formula: P = P_last x (1 + lambda x r); Q = β x r x cash / P.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMMomentumInvestor`

```text
LLM-powered MomentumInvestor: trend following strategy. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMMomentumInvestor`

```text
Hybrid rule+LLM MomentumInvestor: following trend signals. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMMomentumInvestor`

```text
RAG-augmented MomentumInvestor: trend following with retrieved knowledge. Theory: simulation-bases.md Section 4.1.
```
