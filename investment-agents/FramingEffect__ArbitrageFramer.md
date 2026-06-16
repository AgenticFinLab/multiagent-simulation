# FramingEffect / Arbitrage Framer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FramingEffect |
| Agent type | Arbitrage Framer |
| Canonical class | `ArbitrageFramer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: The ArbitrageFramer exploits the persistent mispricing created by framing-biased agents. Functionally identical to FrameInvariantTrader in decision logic (both contrarian at 5% threshold), but conceptually distinct: where FrameInvariantTrader acts from rational valuation, ArbitrageFramer explicitly targets the spread between biased market price and fundamental value. Together they form the rational stabilizing block.

## Financial Theory / Theoretical Basis

### Rule / `ArbitrageFramer`
- Theory: simulation-bases.md Section 4.4 -- ArbitrageFramer
- Theoretical basis: Framing arbitrage (Kuhberger, 1998).

### LLM / `LLMArbitrageFramer`
- LLM-driven ArbitrageFramer: exploits framing-induced mispricing. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMArbitrageFramer`
- RuleLLM-driven ArbitrageFramer: exploits framing-induced mispricing. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMArbitrageFramer`
- RAG-augmented ArbitrageFramer: exploits framing-induced mispricing. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FramingEffect.LLM.prompts:LLM_ARBITRAGE_FRAMER_SYS', 'user_message': 'examples.FramingEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_ARBITRAGE_FRAMER_SYS', 'user_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FramingEffect.Rag.prompts:RAGLLM_ARBITRAGE_FRAMER_SYS', 'user_message': 'examples.FramingEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `500` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| spread_threshold | Rule: `0.05` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | arbitrageframer | ArbitrageFramer | `ArbitrageFramer` | 1 | `examples/FramingEffect/Rule/players.py` |
| LLM | arbitrageframer | ArbitrageFramer | `LLMArbitrageFramer` | 1 | `examples/FramingEffect/LLM/players.py` |
| RuleLLM | arbitrageframer | ArbitrageFramer | `RuleLLMArbitrageFramer` | 1 | `examples/FramingEffect/RuleLLM/players.py` |
| Rag | arbitrageframer | ArbitrageFramer | `RagLLMArbitrageFramer` | 1 | `examples/FramingEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ArbitrageFramer

**Summary**: The ArbitrageFramer exploits the persistent mispricing created by framing-biased agents. Functionally identical to FrameInvariantTrader in decision logic (both contrarian at 5% threshold), but conceptually distinct: where FrameInvariantTrader acts from rational valuation, ArbitrageFramer explicitly targets the spread between biased market price and fundamental value. Together they form the rational stabilizing block.

**Theoretical Foundation**: Kuhberger (1998) framing arbitrage; Shleifer & Vishny (1997) limits to arbitrage constraining their maximum positions.

## Source Docstring Excerpts

### Rule / `ArbitrageFramer`

```text
Theory: simulation-bases.md Section 4.4 -- ArbitrageFramer

Theoretical basis: Framing arbitrage (Kuhberger, 1998).
Exploits framing-induced mispricing by recognizing when same data drives different prices.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMArbitrageFramer`

```text
LLM-driven ArbitrageFramer: exploits framing-induced mispricing. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMArbitrageFramer`

```text
RuleLLM-driven ArbitrageFramer: exploits framing-induced mispricing. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMArbitrageFramer`

```text
RAG-augmented ArbitrageFramer: exploits framing-induced mispricing. Theory: simulation-bases.md Section 4.4.
```
