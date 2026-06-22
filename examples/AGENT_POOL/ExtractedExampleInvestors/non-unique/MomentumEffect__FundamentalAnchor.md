# MomentumEffect / Fundamental Anchor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MomentumEffect |
| Agent type | Fundamental Anchor |
| Canonical class | `FundamentalAnchor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trades against mispricing relative to fundamental value. **Theoretical and Empirical Basis**: Fundamental-value anchoring and limits of arbitrage. **Design Purpose**: Provide long-run gravity against trend overshoot. **Behavioral Framework**: Rule uses `value_threshold=0.05`, `scale=1.5`, `max_position=50.0`. **Decision Process**: Buy undervaluation and sell overvaluation once mispricing exceeds threshold. **Worked Numerical Example**: Price 8% below fundamental triggers a buy. **Academic References**: Shleifer and Vishny (1997), DOI: 10.1111/j.1540-6261.1997.tb03807.x.

## Financial Theory / Theoretical Basis

### LLM / `LLMFundamentalAnchor`
- LLM FundamentalAnchor. Theory: simulation-bases.md Section 4.6.

### RuleLLM / `RuleLLMFundamentalAnchor`
- Hybrid FundamentalAnchor. Theory: simulation-bases.md Section 4.6.

### Rag / `RagLLMFundamentalAnchor`
- RAG FundamentalAnchor. Theory: simulation-bases.md Section 4.6.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, RuleLLM |
| initial_cash | LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, RuleLLM |
| initial_position | LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MomentumEffect.LLM.prompts:LLM_FUNDAMENTAL_SYS', 'user_message': 'examples.MomentumEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_FUNDAMENTAL_ANCHOR_SYS', 'user_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_FUNDAMENTAL_ANCHOR_SYS', 'user_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_fundamental | LLM Fundamental Anchor | `LLMFundamentalAnchor` | 2 | `examples/MomentumEffect/LLM/players.py` |
| RuleLLM | rulellm_fundamental | RuleLLM Fundamental Anchor | `RuleLLMFundamentalAnchor` | 2 | `examples/MomentumEffect/RuleLLM/players.py` |
| Rag | ragllm_fundamental | RAG Fundamental Anchor | `RagLLMFundamentalAnchor` | 2 | `examples/MomentumEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.6 FundamentalTrader / FundamentalAnchor

**Summary**: Trades against mispricing relative to fundamental value.  
**Theoretical and Empirical Basis**: Fundamental-value anchoring and limits of
arbitrage.  
**Design Purpose**: Provide long-run gravity against trend overshoot.  
**Behavioral Framework**: Rule uses `value_threshold=0.05`, `scale=1.5`,
`max_position=50.0`.  
**Decision Process**: Buy undervaluation and sell overvaluation once mispricing
exceeds threshold.  
**Worked Numerical Example**: Price 8% below fundamental triggers a buy.  
**Academic References**: Shleifer and Vishny (1997), DOI:
10.1111/j.1540-6261.1997.tb03807.x.

## Source Docstring Excerpts

### LLM / `LLMFundamentalAnchor`

```text
LLM FundamentalAnchor. Theory: simulation-bases.md Section 4.6.
```

### RuleLLM / `RuleLLMFundamentalAnchor`

```text
Hybrid FundamentalAnchor. Theory: simulation-bases.md Section 4.6.
```

### Rag / `RagLLMFundamentalAnchor`

```text
RAG FundamentalAnchor. Theory: simulation-bases.md Section 4.6.
```
