# CarryTradeUnwind / Carry Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CarryTradeUnwind |
| Agent type | Carry Trader |
| Canonical class | `CarryTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

- **Citation**: Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). "Carry trades and currency crashes." *NBER Macroeconomics Annual*, 23(1), 313-347. DOI: 10.1086/593088 - **Core Insight**: Carry trades earn positive returns on average (the "carry premium") but exhibit severe negative skewness -- they are vulnerable to sudden, large losses when risk sentiment reverses and funding currencies appreciate sharply. Brunnermeier et al. document a pattern they call "going up by the stairs and coming down by the elevator": slow carry accumulation during risk-on periods, sudden violent unwind during risk-off. The crash occurs because all carry traders unwind simultaneously, creating herding sell pressure on target currencies. - **Mathematical Formulation**: Expected carry return: E[r_carry] = i_high - i_low (interest rate differential). Crash risk: Prob(unwind | risk_off) x DeltaP_unwind >> E[r_carry]. The carry crash skewness κ < -1, meaning crash losses are systematically larger than normal gains. Leverage amplification: effective price move = lambda x (N_carry x sell_qty), where N_carry = number of carry traders. - **Empirical Evidence**: Brunnermeier et al. (2009) document that carry trade returns have skewness of -1.5 to -2.0, with crash months averaging -5% to -15% returns vs. normal months of +0.3% to +0.8%. The 2008 JPY carry unwind saw USD/JPY fall from 110 to 88 (-20%) in 6 weeks, consistent with the simulation's target drawdown of 10-25%. - **Relevance to Investor Taxonomy**: CarryTrader represents the slow accumulation phase; LeveragedCarryFund represents the violent unwind; their interaction generates the asymmetric crash pattern documented by Brunnermeier et al.

## Financial Theory / Theoretical Basis

### Rule / `CarryTrader`
- Theory: simulation-bases.md Section 4.1 -- CarryTrader
- Theoretical basis: Uncovered interest parity deviation (Brunnermeier et al., 2009);

### LLM / `LLMCarryTrader`
- LLM-driven carry trader -- borrows low-yield, invests high-yield. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMCarryTrader`
- RuleLLM-driven carry trader -- borrows low-yield, invests high-yield. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMCarryTrader`
- RAG-augmented carry trader -- borrows low-yield, invests high-yield. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| carry_size | Rule: `100.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500.0`<br>LLM: `500.0`<br>RuleLLM: `500.0`<br>Rag: `500.0` | LLM, Rag, Rule, RuleLLM |
| leverage | Rule: `5.0` | Rule |
| llm | LLM: `{'sys_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_CARRY_TRADER_SYS', 'user_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_CARRY_TRADER_SYS', 'user_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_CARRY_TRADER_SYS', 'user_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| unwind_threshold | Rule: `0.02` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | carry_trader | Carry Trader | `CarryTrader` | 2 | `examples/CarryTradeUnwind/Rule/players.py` |
| LLM | llm_carry_trader | LLM Carry Trader | `LLMCarryTrader` | 2 | `examples/CarryTradeUnwind/LLM/players.py` |
| RuleLLM | rulellm_carry_trader | RuleLLM Carry Trader | `RuleLLMCarryTrader` | 2 | `examples/CarryTradeUnwind/RuleLLM/players.py` |
| Rag | ragllm_carry_trader | RAG Carry Trader | `RagLLMCarryTrader` | 2 | `examples/CarryTradeUnwind/Rag/players.py` |

## Scenario-Theory Excerpts

### 2.1 Carry Trade Returns and Crash Risk (Brunnermeier, Nagel & Pedersen)

- **Citation**: Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). "Carry trades and currency crashes." *NBER Macroeconomics Annual*, 23(1), 313-347. DOI: 10.1086/593088
- **Core Insight**: Carry trades earn positive returns on average (the "carry premium") but exhibit severe negative skewness -- they are vulnerable to sudden, large losses when risk sentiment reverses and funding currencies appreciate sharply. Brunnermeier et al. document a pattern they call "going up by the stairs and coming down by the elevator": slow carry accumulation during risk-on periods, sudden violent unwind during risk-off. The crash occurs because all carry traders unwind simultaneously, creating herding sell pressure on target currencies.
- **Mathematical Formulation**: Expected carry return: E[r_carry] = i_high - i_low (interest rate differential). Crash risk: Prob(unwind | risk_off) x DeltaP_unwind >> E[r_carry]. The carry crash skewness κ < -1, meaning crash losses are systematically larger than normal gains. Leverage amplification: effective price move = lambda x (N_carry x sell_qty), where N_carry = number of carry traders.
- **Empirical Evidence**: Brunnermeier et al. (2009) document that carry trade returns have skewness of -1.5 to -2.0, with crash months averaging -5% to -15% returns vs. normal months of +0.3% to +0.8%. The 2008 JPY carry unwind saw USD/JPY fall from 110 to 88 (-20%) in 6 weeks, consistent with the simulation's target drawdown of 10-25%.
- **Relevance to Investor Taxonomy**: CarryTrader represents the slow accumulation phase; LeveragedCarryFund represents the violent unwind; their interaction generates the asymmetric crash pattern documented by Brunnermeier et al.

## Source Docstring Excerpts

### Rule / `CarryTrader`

```text
Borrows low-yield currency to invest in high-yield -- profits from interest differential.

Theory: simulation-bases.md Section 4.1 -- CarryTrader
Theoretical basis: Uncovered interest parity deviation (Brunnermeier et al., 2009);
unwinds aggressively when funding currency appreciates, destabilizing exchange rates.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMCarryTrader`

```text
LLM-driven carry trader -- borrows low-yield, invests high-yield. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMCarryTrader`

```text
RuleLLM-driven carry trader -- borrows low-yield, invests high-yield. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMCarryTrader`

```text
RAG-augmented carry trader -- borrows low-yield, invests high-yield. Theory: simulation-bases.md Section 4.1.
```
