# GamblerFallacy / Hot Hand Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GamblerFallacy |
| Agent type | Hot Hand Trader |
| Canonical class | `HotHandTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Represents momentum investors and retail traders who believe that a market "on a streak" will continue in that direction. It is intentionally action-aligned with StreakReversalTrader in the current implementation: positive deviation triggers buying and negative deviation triggers selling, but the interpretation is continuation rather than reversal.

## Financial Theory / Theoretical Basis

### Rule / `HotHandTrader`
- Theory: simulation-bases.md Section 4.2 -- HotHandTrader
- Theoretical basis: Hot hand fallacy (Gilovich et al., 1985).

### LLM / `LLMHotHandTrader`
- LLM-driven HotHandTrader: believes winning streaks will continue. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMHotHandTrader`
- RuleLLM-driven HotHandTrader: believes winning streaks will continue. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMHotHandTrader`
- RagLLM-driven hot hand trader: believes in streak continuation. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| activation_threshold | Rule: `0.02` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GamblerFallacy.LLM.prompts:LLM_HOT_HAND_TRADER_SYS', 'user_message': 'examples.GamblerFallacy.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GamblerFallacy.RuleLLM.prompts:RULELLM_HOT_HAND_TRADER_SYS', 'user_message': 'examples.GamblerFallacy.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GamblerFallacy.Rag.prompts:RAGLLM_HOT_HAND_TRADER_SYS', 'user_message': 'examples.GamblerFallacy.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `800`<br>LLM: `800`<br>RuleLLM: `800`<br>Rag: `800` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `5000` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | hothandtrader | HotHandTrader | `HotHandTrader` | 2 | `examples/GamblerFallacy/Rule/players.py` |
| LLM | hothandtrader | HotHandTrader | `LLMHotHandTrader` | 2 | `examples/GamblerFallacy/LLM/players.py` |
| RuleLLM | hothandtrader | HotHandTrader | `RuleLLMHotHandTrader` | 2 | `examples/GamblerFallacy/RuleLLM/players.py` |
| Rag | hothandtrader | HotHandTrader | `RagLLMHotHandTrader` | 2 | `examples/GamblerFallacy/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 HotHandTrader

**Summary**: Represents momentum investors and retail traders who believe that a market "on a streak" will continue in that direction. It is intentionally action-aligned with StreakReversalTrader in the current implementation: positive deviation triggers buying and negative deviation triggers selling, but the interpretation is continuation rather than reversal.

**Theoretical and Empirical Basis**: Gilovich, Vallone & Tversky (1985) Hot Hand belief; Jegadeesh & Titman (1993) momentum returns; Daniel, Hirshleifer & Subrahmanyam (1998) behavioral momentum.

**Design Purpose**: Separates the belief narrative from the order-flow direction. Together with StreakReversalTrader, it creates co-directional biased pressure that can dominate rational correction when deviations are salient.

**Behavioral Framework**: Uses the same market state and config-controlled `activation_threshold`, `quantity_scale`, and `max_order` fields under `configs/GamblerFallacy/Rule/players.yml -> hothandtrader.config.extras`.

**Decision Process**:
1. Hold when the deviation magnitude is below the activation threshold.
2. Buy when price is above fundamental, interpreting the deviation as upward momentum.
3. Sell when price is below fundamental, interpreting the deviation as downward momentum.
4. Cap quantity by `max_order`, cash, and current position.

**Worked Numerical Example**: With `deviation = -0.03`, `activation_threshold = 0.02`, `quantity_scale = 5000`, and `max_order = 800`, desired quantity is 150; the trader sells up to 150 shares if it holds enough inventory.

**Academic References**: Gilovich et al. (1985), Jegadeesh & Titman (1993), Daniel et al. (1998). See Section 2.2 and Section 8.1.

## Source Docstring Excerpts

### Rule / `HotHandTrader`

```text
Theory: simulation-bases.md Section 4.2 -- HotHandTrader

Theoretical basis: Hot hand fallacy (Gilovich et al., 1985).
Believes winning streaks will continue, over-betting on recent winners.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMHotHandTrader`

```text
LLM-driven HotHandTrader: believes winning streaks will continue. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMHotHandTrader`

```text
RuleLLM-driven HotHandTrader: believes winning streaks will continue. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMHotHandTrader`

```text
RagLLM-driven hot hand trader: believes in streak continuation. Theory: simulation-bases.md Section 4.2.
```
