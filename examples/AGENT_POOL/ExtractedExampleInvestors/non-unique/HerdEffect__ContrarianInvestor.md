# HerdEffect / Contrarian Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HerdEffect |
| Agent type | Contrarian Investor |
| Canonical class | `ContrarianInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements De Bondt & Thaler (1985) mean-reversion contrarian strategy. Buys when P < F, sells when P > F. Bids around fundamental (from own extras, not broadcast). Primary stabilizing force.

## Financial Theory / Theoretical Basis

### Rule / `ContrarianInvestor`
- Theory: simulation-bases.md Section 4.2 -- ContrarianInvestor
- Theoretical basis: Contrarian / value strategy (De Bondt & Thaler, 1985).
- Formula: P = F + epsilon; Q = β x (F - P) / P x cash / P.

### LLM / `LLMContrarianInvestor`
- LLM-powered ContrarianInvestor: value investing against the crowd. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMContrarianInvestor`
- Hybrid rule+LLM ContrarianInvestor: betting against the crowd. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMContrarianInvestor`
- RAG-augmented ContrarianInvestor: value investing with retrieved knowledge. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `calculate_bid`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| beta | Rule: `0.5` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental | Rule: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HerdEffect.LLM.prompts:LLM_CONTRARIAN_SYS', 'user_message': 'examples.HerdEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_CONTRARIAN_SYS', 'user_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_CONTRARIAN_SYS', 'user_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| noise_std | Rule: `0.5` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | investor_contrarian | Contrarian Investor | `ContrarianInvestor` | 2 | `examples/HerdEffect/Rule/players.py` |
| LLM | llm_contrarian | LLM Contrarian Investor | `LLMContrarianInvestor` | 2 | `examples/HerdEffect/LLM/players.py` |
| RuleLLM | rulellm_contrarian | RuleLLM Contrarian Investor | `RuleLLMContrarianInvestor` | 2 | `examples/HerdEffect/RuleLLM/players.py` |
| Rag | ragllm_contrarian | RAG Contrarian Investor | `RagLLMContrarianInvestor` | 2 | `examples/HerdEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 ContrarianInvestor

**Summary**: Implements De Bondt & Thaler (1985) mean-reversion contrarian strategy. Buys when P < F, sells when P > F. Bids around fundamental (from own extras, not broadcast). Primary stabilizing force.

**Foundation**: De Bondt & Thaler (1985) overreaction/reversal; Graham & Dodd fundamental value investing. `doi:10.1111/j.1540-6261.1985.tb05004.x`

**Design Purpose**: Provide the mean-reversion force that eventually terminates the momentum episode. The only agent with direct fundamental value access -- all others respond only to price signals.

**Behavioral Framework**:

| Decision Variable | Logic                      | Formula                              |
|-------------------|----------------------------|--------------------------------------|
| Bid price         | Fundamental with noise     | `F + N(0, noise_std)`                |
| Quantity          | Fundamental gap x capital  | `β x (F - P) / P x cash / bid_price` |
| Buy condition     | P < F (market undervalued) | qty > 0                              |
| Sell condition    | P > F (market overvalued)  | qty < 0                              |
| Position cap      | ±50 shares                 | Hard limit                           |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. Read `fundamental` from own `extras` (NOT from broadcast -- HerdEffect market does not broadcast it)
3. `bid_price = fundamental + N(0, noise_std)`
4. `qty = beta x (fundamental - P) / P x cash / bid_price`; clip to [-50, +50]
5. Update cash/position; send order

**Worked Example** (beta=0.5, noise_std=0.5, cash=10,000, F=100, P=115):
- bid_price = 100 + 0.4 = 100.4
- qty = 0.5 x (100 - 115) / 115 x 10,000 / 100.4 = -6.49 -> -6 shares (sell)
- Interpretation: Sells 6 shares; resists momentum overvaluation

**References**: simulation-bases.md Section 2 Theory 2; `doi:10.1111/j.1540-6261.1985.tb05004.x`

---

## Source Docstring Excerpts

### Rule / `ContrarianInvestor`

```text
Theory: simulation-bases.md Section 4.2 -- ContrarianInvestor

Theoretical basis: Contrarian / value strategy (De Bondt & Thaler, 1985).
Formula: P = F + epsilon; Q = β x (F - P) / P x cash / P.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMContrarianInvestor`

```text
LLM-powered ContrarianInvestor: value investing against the crowd. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMContrarianInvestor`

```text
Hybrid rule+LLM ContrarianInvestor: betting against the crowd. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMContrarianInvestor`

```text
RAG-augmented ContrarianInvestor: value investing with retrieved knowledge. Theory: simulation-bases.md Section 4.2.
```
