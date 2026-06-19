# GamblerFallacy / Streak Reversal Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GamblerFallacy |
| Agent type | Streak Reversal Trader |
| Canonical class | `StreakReversalTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Represents retail investors and gamblers who apply the gambler's fallacy to financial markets -- believing that after consecutive price moves in one direction, a reversal is "overdue." In this simplified market encoding, current deviation from fundamental is the observable proxy for perceived streak pressure. The implemented action follows the sign of the deviation, so the agent amplifies the current price state while rationalizing the trade as an overdue-reversal bet.

## Financial Theory / Theoretical Basis

### Rule / `StreakReversalTrader`
- Theory: simulation-bases.md Section 4.1 -- StreakReversalTrader
- Theoretical basis: Law of small numbers misconception (Tversky & Kahneman, 1971).

### LLM / `LLMStreakReversalTrader`
- LLM-driven StreakReversalTrader: expects reversals after consecutive moves. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMStreakReversalTrader`
- RuleLLM-driven StreakReversalTrader: expects reversals after consecutive moves. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMStreakReversalTrader`
- RagLLM-driven streak reversal trader: expects reversals after consecutive moves. Theory: simulation-bases.md Section 4.1.

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
| llm | LLM: `{'sys_message': 'examples.GamblerFallacy.LLM.prompts:LLM_STREAK_REVERSAL_TRADER_SYS', 'user_message': 'examples.GamblerFallacy.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GamblerFallacy.RuleLLM.prompts:RULELLM_STREAK_REVERSAL_TRADER_SYS', 'user_message': 'examples.GamblerFallacy.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GamblerFallacy.Rag.prompts:RAGLLM_STREAK_REVERSAL_TRADER_SYS', 'user_message': 'examples.GamblerFallacy.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `800`<br>LLM: `800`<br>RuleLLM: `800`<br>Rag: `800` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `5000` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | streakreversaltrader | StreakReversalTrader | `StreakReversalTrader` | 2 | `examples/GamblerFallacy/Rule/players.py` |
| LLM | streakreversaltrader | StreakReversalTrader | `LLMStreakReversalTrader` | 2 | `examples/GamblerFallacy/LLM/players.py` |
| RuleLLM | streakreversaltrader | StreakReversalTrader | `RuleLLMStreakReversalTrader` | 2 | `examples/GamblerFallacy/RuleLLM/players.py` |
| Rag | streakreversaltrader | StreakReversalTrader | `RagLLMStreakReversalTrader` | 2 | `examples/GamblerFallacy/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 StreakReversalTrader

**Summary**: Represents retail investors and gamblers who apply the gambler's fallacy to financial markets -- believing that after consecutive price moves in one direction, a reversal is "overdue." In this simplified market encoding, current deviation from fundamental is the observable proxy for perceived streak pressure. The implemented action follows the sign of the deviation, so the agent amplifies the current price state while rationalizing the trade as an overdue-reversal bet.

**Theoretical and Empirical Basis**: Tversky & Kahneman (1971) Law of Small Numbers; Rabin (2002) formal belief model; Croson & Sundali (2005) field validation of streak-conditioned betting distortions.

**Design Purpose**: Provides the primary biased reversal-belief population. Its trades increase demand when the market is above fundamental and increase sell pressure when below fundamental, making the bias visible in aggregate price paths.

**Behavioral Framework**: Reads `deviation = (price - fundamental) / fundamental`, activates when `abs(deviation)` exceeds `configs/GamblerFallacy/Rule/players.yml -> streakreversaltrader.config.extras.activation_threshold`, and sizes orders with `quantity_scale` and `max_order`.

**Decision Process**:
1. If `abs(deviation) <= activation_threshold`, hold.
2. If `deviation > 0`, buy `min(max_order, int(abs(deviation) * quantity_scale))`, capped by available cash.
3. If `deviation < 0`, sell the same capped quantity, capped by current holdings.

**Worked Numerical Example**: With `deviation = 0.04`, `activation_threshold = 0.02`, `quantity_scale = 5000`, and `max_order = 800`, desired quantity is `min(800, int(0.04 * 5000)) = 200`; the trader buys 200 shares if cash permits.

**Academic References**: Tversky & Kahneman (1971), Rabin (2002), Croson & Sundali (2005). See Section 2.1 and Section 8.2 for calibration rationale.

## Source Docstring Excerpts

### Rule / `StreakReversalTrader`

```text
Theory: simulation-bases.md Section 4.1 -- StreakReversalTrader

Theoretical basis: Law of small numbers misconception (Tversky & Kahneman, 1971).
Expects reversals after consecutive price moves, betting against streaks.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMStreakReversalTrader`

```text
LLM-driven StreakReversalTrader: expects reversals after consecutive moves. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMStreakReversalTrader`

```text
RuleLLM-driven StreakReversalTrader: expects reversals after consecutive moves. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMStreakReversalTrader`

```text
RagLLM-driven streak reversal trader: expects reversals after consecutive moves. Theory: simulation-bases.md Section 4.1.
```
