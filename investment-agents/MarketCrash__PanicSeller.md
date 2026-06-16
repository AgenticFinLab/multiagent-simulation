# MarketCrash / Panic Seller

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MarketCrash |
| Agent type | Panic Seller |
| Canonical class | `PanicSeller` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A loss-sensitive investor that sells after drawdowns or sharp one-round drops. **Theoretical and Empirical Basis**: Behavioral loss aversion and feedback trading can amplify market declines. **Design Purpose**: Add discretionary crash amplification beyond mechanical deleveraging. **Behavioral Framework**: Uses loss threshold, crash trigger, and panic-sell fraction. **Decision Process**: Track price losses; if cumulative or one-round losses cross the trigger, sell a configured fraction of holdings. **Worked Numerical Example**: With a 10% loss threshold and 50% panic fraction, a 15% drawdown can trigger sale of half the current position. **Academic References**: Kahneman and Tversky (1979, DOI: 10.2307/1914185); Shiller (1984, DOI: 10.2307/2327670).

## Financial Theory / Theoretical Basis

### Rule / `PanicSeller`
- Theory: simulation-bases.md Section 4.5.

### LLM / `LLMPanicSeller`
- LLM PanicSeller. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMPanicSeller`
- Hybrid PanicSeller. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMPanicSeller`
- RAG PanicSeller. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| crash_trigger | Rule: `-0.03` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `25.0`<br>LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MarketCrash.LLM.prompts:LLM_PANIC_SELLER_SYS', 'user_message': 'examples.MarketCrash.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_PANIC_SELLER_SYS', 'user_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_PANIC_SELLER_SYS', 'user_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| loss_threshold | Rule: `0.1` | Rule |
| panic_sell_fraction | Rule: `0.5` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | panic_seller | Panic Seller | `PanicSeller` | 3 | `examples/MarketCrash/Rule/players.py` |
| LLM | llm_panic_seller | LLM Panic Seller | `LLMPanicSeller` | 3 | `examples/MarketCrash/LLM/players.py` |
| RuleLLM | rulellm_panic_seller | RuleLLM Panic Seller | `RuleLLMPanicSeller` | 3 | `examples/MarketCrash/RuleLLM/players.py` |
| Rag | ragllm_panic_seller | RAG Panic Seller | `RagLLMPanicSeller` | 3 | `examples/MarketCrash/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 PanicSeller

**Summary**: A loss-sensitive investor that sells after drawdowns or sharp
one-round drops.
**Theoretical and Empirical Basis**: Behavioral loss aversion and feedback
trading can amplify market declines.
**Design Purpose**: Add discretionary crash amplification beyond mechanical
deleveraging.
**Behavioral Framework**: Uses loss threshold, crash trigger, and panic-sell
fraction.
**Decision Process**: Track price losses; if cumulative or one-round losses
cross the trigger, sell a configured fraction of holdings.
**Worked Numerical Example**: With a 10% loss threshold and 50% panic fraction,
a 15% drawdown can trigger sale of half the current position.
**Academic References**: Kahneman and Tversky (1979, DOI:
10.2307/1914185); Shiller (1984, DOI: 10.2307/2327670).

## Source Docstring Excerpts

### Rule / `PanicSeller`

```text
Panic seller triggered by losses.

Theory: simulation-bases.md Section 4.5.

Parameters from config extras:
    - loss_threshold, crash_trigger, panic_sell_fraction
```

### LLM / `LLMPanicSeller`

```text
LLM PanicSeller. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMPanicSeller`

```text
Hybrid PanicSeller. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMPanicSeller`

```text
RAG PanicSeller. Theory: simulation-bases.md Section 4.5.
```
