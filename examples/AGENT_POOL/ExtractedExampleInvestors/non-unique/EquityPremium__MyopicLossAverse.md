# EquityPremium / Myopic Loss Averse

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EquityPremium |
| Agent type | Myopic Loss Averse |
| Canonical class | `MyopicLossAverse` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM, Rag |

## Definition and Goal

**Information set**: `stock_price`, `stock_history` (rolling `evaluation_window` entries), `stock_return`

## Financial Theory / Theoretical Basis

### LLM / `LLMMyopicLossAverse`
- LLM-driven myopic loss averse -- frequent evaluation with high loss sensitivity via LLM. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMMyopicLossAverse`
- RuleLLM myopic loss-averse allocator. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMMyopicLossAverse`
- RAG myopic loss-averse allocator. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, RuleLLM |
| initial_bond_ratio | LLM: `0.25`<br>RuleLLM: `0.25`<br>Rag: `0.25` | LLM, Rag, RuleLLM |
| initial_cash | LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, RuleLLM |
| initial_cash_ratio | LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, RuleLLM |
| initial_stock_shares | LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EquityPremium.LLM.prompts:LLM_MYOPIC_LOSS_AVERSE_SYS', 'user_message': 'examples.EquityPremium.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.EquityPremium.RuleLLM.prompts:RULELLM_MYOPIC_LOSS_AVERSE_INVESTOR_SYS', 'user_message': 'examples.EquityPremium.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.EquityPremium.Rag.prompts:RAGLLM_MYOPIC_LOSS_AVERSE_INVESTOR_SYS', 'user_message': 'examples.EquityPremium.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_myopic | LLM Myopic Loss-Averse | `LLMMyopicLossAverse` | 5 | `examples/EquityPremium/LLM/players.py` |
| RuleLLM | rulellm_myopic | RuleLLM Myopic Loss-Averse | `RuleLLMMyopicLossAverse` | 5 | `examples/EquityPremium/RuleLLM/players.py` |
| Rag | ragllm_myopic | RAG Myopic Loss-Averse | `RagLLMMyopicLossAverse` | 5 | `examples/EquityPremium/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 MyopicLossAverseInvestor

#### Summary
Evaluates portfolio over a short rolling window, overweighting recent losses. Frequent negative realizations drive extreme equity risk aversion, demanding high premiums before holding stocks.

#### Theoretical and Empirical Foundation
- **Benartzi & Thaler (1995)**: Myopic loss aversion. Investors who evaluate over 1-year horizons and have lambda ≈ 2.25 demand ~6% equity premium. DOI: `https://doi.org/10.2307/2118511`
- **Kahneman & Tversky (1979)**: Prospect theory. Loss aversion coefficient lambda ≈ 2-2.5 drives asymmetric evaluation. DOI: `https://doi.org/10.2307/1914185`

#### Design Purpose and Activation Scenarios
- **Activates when**: Rolling window loss probability is high (recent negative returns)
- **Role in phenomenon**: Amplifies equity risk premium; primary driver of the puzzle in simulation
- **Interaction effects**: Reduces net stock demand, driving price below fundamental; counterbalanced by LongHorizonInvestor

#### Behavioral Framework

**Information set**: `stock_price`, `stock_history` (rolling `evaluation_window` entries), `stock_return`

**Mechanism narrative**: Computes recent return volatility and loss probability over a short window. Multiplies volatility by a loss-aversion-weighted factor. Sets target stock allocation inversely proportional to perceived risk. Adjusts toward target gradually (30% of gap per round).

**Mathematical model**:
```
returns = [r_t-1, r_t-2, ..., r_t-evaluation_window]
vol = std(returns)
loss_prob = count(r < 0) / evaluation_window
perceived_risk = vol x (1 + loss_aversion x loss_prob)
target_stock_pct = max(0.1, 0.5 - risk_aversion x perceived_risk)
stock_qty = (target_value - current_value) / price x 0.3
```

**Behavioral properties**: Bounded rationality; myopic evaluation horizon; loss aversion (lambda > 1)

#### Decision Process Walkthrough

1. Observe `stock_price` and retrieve `stock_history` for last `evaluation_window` rounds
2. Compute `vol` and `loss_prob` from return series
3. Compute `perceived_risk = vol x (1 + loss_aversion x loss_prob)`
4. Compute `target_stock_pct = max(0.1, 0.5 - risk_aversion x perceived_risk)`
5. Submit stock_qty adjustment (clamped to [-10, +10])

#### Worked Numerical Example

Given: price = 105, evaluation_window = 5, recent returns = [-0.02, -0.01, 0.01, -0.02, 0.00]
- vol = 0.013, loss_prob = 0.6
- loss_aversion = 2.25, risk_aversion = 3
- perceived_risk = 0.013 x (1 + 2.25 x 0.6) = 0.031
- target_stock_pct = max(0.1, 0.5 - 3 x 0.031) = 0.407
- stock_qty = (0.407 x portfolio_value - current_stock_value) / 105 x 0.3 -> sell signal

#### Academic References
- Benartzi, S., & Thaler, R. H. (1995). *Myopic loss aversion and the equity premium puzzle*. QJE. DOI: https://doi.org/10.2307/2118511

---

## Source Docstring Excerpts

### LLM / `LLMMyopicLossAverse`

```text
LLM-driven myopic loss averse -- frequent evaluation with high loss sensitivity via LLM. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMMyopicLossAverse`

```text
RuleLLM myopic loss-averse allocator. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMMyopicLossAverse`

```text
RAG myopic loss-averse allocator. Theory: simulation-bases.md Section 4.1.
```
