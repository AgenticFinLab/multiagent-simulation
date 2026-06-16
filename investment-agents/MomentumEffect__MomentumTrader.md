# MomentumEffect / Momentum Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MomentumEffect |
| Agent type | Momentum Trader |
| Canonical class | `MomentumTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Buys after positive recent returns and sells after negative recent returns. **Theoretical and Empirical Basis**: Return momentum and positive-feedback trading. **Design Purpose**: Create the core continuation pressure. **Behavioral Framework**: Rule uses `lookback_window=5`, `momentum_threshold=0.02`, `scale=3.0`, `max_position=100.0`. **Decision Process**: Trade in the direction of the 5-period momentum signal once it exceeds the threshold. **Worked Numerical Example**: A 4% positive momentum signal exceeds the 2% threshold and triggers a buy scaled by signal strength. **Academic References**: Jegadeesh and Titman (1993), DOI: 10.1111/j.1540-6261.1993.tb04702.x.

## Financial Theory / Theoretical Basis

### Rule / `MomentumTrader`
- Theory: simulation-bases.md Section 4.1.
- Formula:
- Financial Theory:
- - Conservatism Bias: Investors underreact to news
- - Information Diffusion: News spreads gradually
- - Self-attribution Bias: Winners attribute success to skill

### LLM / `LLMMomentumTrader`
- LLM MomentumTrader. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMMomentumTrader`
- Hybrid MomentumTrader. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMMomentumTrader`
- RAG MomentumTrader. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `_hold_order`, `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MomentumEffect.LLM.prompts:LLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.MomentumEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback_window | Rule: `5` | Rule |
| max_position | Rule: `100.0` | Rule |
| momentum_threshold | Rule: `0.02` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| scale | Rule: `3.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentum_trader | Momentum Trader | `MomentumTrader` | 3 | `examples/MomentumEffect/Rule/players.py` |
| LLM | llm_momentum_trader | LLM Momentum Trader | `LLMMomentumTrader` | 3 | `examples/MomentumEffect/LLM/players.py` |
| RuleLLM | rulellm_momentum_trader | RuleLLM Momentum Trader | `RuleLLMMomentumTrader` | 3 | `examples/MomentumEffect/RuleLLM/players.py` |
| Rag | ragllm_momentum_trader | RAG Momentum Trader | `RagLLMMomentumTrader` | 3 | `examples/MomentumEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 MomentumTrader

**Summary**: Buys after positive recent returns and sells after negative recent
returns.  
**Theoretical and Empirical Basis**: Return momentum and positive-feedback
trading.  
**Design Purpose**: Create the core continuation pressure.  
**Behavioral Framework**: Rule uses `lookback_window=5`,
`momentum_threshold=0.02`, `scale=3.0`, `max_position=100.0`.  
**Decision Process**: Trade in the direction of the 5-period momentum signal
once it exceeds the threshold.  
**Worked Numerical Example**: A 4% positive momentum signal exceeds the 2%
threshold and triggers a buy scaled by signal strength.  
**Academic References**: Jegadeesh and Titman (1993), DOI:
10.1111/j.1540-6261.1993.tb04702.x.

## Source Docstring Excerpts

### Rule / `MomentumTrader`

```text
Momentum Strategy (Jegadeesh & Titman 1993):
    Buy assets with positive past returns (winners)
    Sell assets with negative past returns (losers)

Theory: simulation-bases.md Section 4.1.

Formula:
    signal = weighted average of past N returns
    Q = scale x signal x (max_position - current_position) if signal > threshold

Financial Theory:
    - Conservatism Bias: Investors underreact to news
    - Information Diffusion: News spreads gradually
    - Self-attribution Bias: Winners attribute success to skill

Parameters from config extras:
    - lookback_window, momentum_threshold, scale, max_position
```

### LLM / `LLMMomentumTrader`

```text
LLM MomentumTrader. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMMomentumTrader`

```text
Hybrid MomentumTrader. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMMomentumTrader`

```text
RAG MomentumTrader. Theory: simulation-bases.md Section 4.1.
```
