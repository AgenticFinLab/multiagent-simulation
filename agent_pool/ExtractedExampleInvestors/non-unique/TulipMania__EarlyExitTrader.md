# TulipMania / Early Exit Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | TulipMania |
| Agent type | Early Exit Trader |
| Canonical class | `EarlyExitTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Participates tactically but exits when speculative excess becomes visible. **Theoretical and Empirical Basis**: Rational bubble riding and strategic liquidation before common exit pressure arrives. **Design Purpose**: Add peak-adjacent selling pressure without redesigning the market as a limit-order book. **Behavioral Framework**: Uses the same overvaluation signal as IntrinsicValueTrader but interprets the sell as early-exit timing. **Decision Process**: If `abs(deviation) > 0.05`, set `quantity = min(500, int(abs(deviation) * 3000))`; buy discounts and sell overvaluation subject to constraints. **Worked Numerical Example**: At price 130 and fundamental 100, deviation is 0.30, so the trader sells up to 500 units if inventory is available. **Academic References**: Historical bubble timing, rational bubble riding, and crash-precursor behavior.

## Financial Theory / Theoretical Basis

### Rule / `EarlyExitTrader`
- Theory: simulation-bases.md Section 4.4
- Theoretical Basis: Rational bubble riding (Thompson, 2007)

### LLM / `LLMEarlyExitTrader`
- Theory: simulation-bases.md Section 4.4

### RuleLLM / `RuleLLMEarlyExitTrader`
- Theory: simulation-bases.md Section 4.4

### Rag / `RagLLMEarlyExitTrader`
- Theory: simulation-bases.md Section 4.4

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| exit_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| exit_threshold | Rule: `0.4`<br>LLM: `0.4`<br>RuleLLM: `0.4`<br>Rag: `0.4` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.TulipMania.LLM.prompts:LLM_EARLY_EXIT_TRADER_SYS', 'user_message': 'examples.TulipMania.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_EARLY_EXIT_TRADER_SYS', 'user_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.TulipMania.Rag.prompts:RAGLLM_EARLY_EXIT_TRADER_SYS', 'user_message': 'examples.TulipMania.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | earlyexittrader | EarlyExitTrader | `EarlyExitTrader` | 2 | `examples/TulipMania/Rule/players.py` |
| LLM | earlyexittrader | EarlyExitTrader | `LLMEarlyExitTrader` | 2 | `examples/TulipMania/LLM/players.py` |
| RuleLLM | earlyexittrader | EarlyExitTrader | `RuleLLMEarlyExitTrader` | 2 | `examples/TulipMania/RuleLLM/players.py` |
| Rag | earlyexittrader | EarlyExitTrader | `RagLLMEarlyExitTrader` | 2 | `examples/TulipMania/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 EarlyExitTrader

**Summary**: Participates tactically but exits when speculative excess becomes
visible.
**Theoretical and Empirical Basis**: Rational bubble riding and strategic
liquidation before common exit pressure arrives.
**Design Purpose**: Add peak-adjacent selling pressure without redesigning the
market as a limit-order book.
**Behavioral Framework**: Uses the same overvaluation signal as
IntrinsicValueTrader but interprets the sell as early-exit timing.
**Decision Process**: If `abs(deviation) > 0.05`, set
`quantity = min(500, int(abs(deviation) * 3000))`; buy discounts and sell
overvaluation subject to constraints.
**Worked Numerical Example**: At price 130 and fundamental 100, deviation is
0.30, so the trader sells up to 500 units if inventory is available.
**Academic References**: Historical bubble timing, rational bubble riding, and
crash-precursor behavior.

## Source Docstring Excerpts

### Rule / `EarlyExitTrader`

```text
Recognizes speculative excess early and exits before the crash.

Theory: simulation-bases.md Section 4.4
Theoretical Basis: Rational bubble riding (Thompson, 2007)
Market Role: stabilizing
```

### LLM / `LLMEarlyExitTrader`

```text
LLM early exit trader recognizing speculative excess and exiting early.

Theory: simulation-bases.md Section 4.4
```

### RuleLLM / `RuleLLMEarlyExitTrader`

```text
Rule+LLM early exit trader recognizing speculative excess and exiting early.

Theory: simulation-bases.md Section 4.4
```

### Rag / `RagLLMEarlyExitTrader`

```text
RAG-augmented early exit trader recognizing speculative excess and exiting early.

Theory: simulation-bases.md Section 4.4
```
