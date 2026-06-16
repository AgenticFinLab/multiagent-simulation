# MomentumEffect / Contrarian Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MomentumEffect |
| Agent type | Contrarian Trader |
| Canonical class | `ContrarianTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trades against recent momentum once the move is large enough. **Theoretical and Empirical Basis**: Overreaction and mean-reversion evidence. **Design Purpose**: Prevent unchecked continuation. **Behavioral Framework**: Rule uses `reversion_threshold=0.03`, `scale=2.0`, `max_position=80.0`. **Decision Process**: Convert the momentum signal into an opposite-side order when the absolute signal exceeds the threshold. **Worked Numerical Example**: A 5% positive momentum signal generates a sell signal. **Academic References**: De Bondt and Thaler (1985), DOI: 10.1111/j.1540-6261.1985.tb05004.x.

## Financial Theory / Theoretical Basis

### Rule / `ContrarianTrader`
- Theory: simulation-bases.md Section 4.2.
- Financial Theory:
- - Overreaction: Markets overshoot and correct
- - Mean reversion: Prices return to fundamentals

### LLM / `LLMContrarianTrader`
- LLM ContrarianTrader. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMContrarianTrader`
- Hybrid ContrarianTrader. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMContrarianTrader`
- RAG ContrarianTrader. Theory: simulation-bases.md Section 4.2.

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
| llm | LLM: `{'sys_message': 'examples.MomentumEffect.LLM.prompts:LLM_CONTRARIAN_SYS', 'user_message': 'examples.MomentumEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_CONTRARIAN_TRADER_SYS', 'user_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_CONTRARIAN_TRADER_SYS', 'user_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_position | Rule: `80.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| reversion_threshold | Rule: `0.03` | Rule |
| scale | Rule: `2.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | contrarian_trader | Contrarian Trader | `ContrarianTrader` | 2 | `examples/MomentumEffect/Rule/players.py` |
| LLM | llm_contrarian | LLM Contrarian Trader | `LLMContrarianTrader` | 2 | `examples/MomentumEffect/LLM/players.py` |
| RuleLLM | rulellm_contrarian | RuleLLM Contrarian Trader | `RuleLLMContrarianTrader` | 2 | `examples/MomentumEffect/RuleLLM/players.py` |
| Rag | ragllm_contrarian | RAG Contrarian Trader | `RagLLMContrarianTrader` | 2 | `examples/MomentumEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 ContrarianTrader

**Summary**: Trades against recent momentum once the move is large enough.  
**Theoretical and Empirical Basis**: Overreaction and mean-reversion evidence.  
**Design Purpose**: Prevent unchecked continuation.  
**Behavioral Framework**: Rule uses `reversion_threshold=0.03`,
`scale=2.0`, `max_position=80.0`.  
**Decision Process**: Convert the momentum signal into an opposite-side order
when the absolute signal exceeds the threshold.  
**Worked Numerical Example**: A 5% positive momentum signal generates a sell
signal.  
**Academic References**: De Bondt and Thaler (1985), DOI:
10.1111/j.1540-6261.1985.tb05004.x.

## Source Docstring Excerpts

### Rule / `ContrarianTrader`

```text
Contrarian Strategy (De Bondt & Thaler 1985):
    Buy past losers, sell past winners
    Exploits overreaction hypothesis

Theory: simulation-bases.md Section 4.2.

Financial Theory:
    - Overreaction: Markets overshoot and correct
    - Mean reversion: Prices return to fundamentals

Parameters from config extras:
    - reversion_threshold, scale, max_position
```

### LLM / `LLMContrarianTrader`

```text
LLM ContrarianTrader. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMContrarianTrader`

```text
Hybrid ContrarianTrader. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMContrarianTrader`

```text
RAG ContrarianTrader. Theory: simulation-bases.md Section 4.2.
```
