# GamblerFallacy / Arbitrageur

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GamblerFallacy |
| Agent type | Arbitrageur |
| Canonical class | `Arbitrageur` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Explicitly targets streak-based mispricing for profit. Functionally identical to IndependentAssessor in decision logic but conceptually represents a dedicated arbitrage strategy rather than passive fundamental investing. Together Section 4.3 and Section 4.4 constitute the rational stabilizing force whose combined capacity determines how quickly fallacy-driven deviations correct.

## Financial Theory / Theoretical Basis

### Rule / `Arbitrageur`
- Theory: simulation-bases.md Section 4.4 -- Arbitrageur
- Theoretical basis: Limits to arbitrage (Shleifer & Vishny, 1997).

### LLM / `LLMArbitrageur`
- LLM-driven Arbitrageur: exploits mispricing caused by streak-based traders. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMArbitrageur`
- RuleLLM-driven Arbitrageur: exploits mispricing from streak-based traders. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMArbitrageur`
- RagLLM-driven arbitrageur: exploits gambler's fallacy mispricing. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| activation_threshold | Rule: `0.05` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GamblerFallacy.LLM.prompts:LLM_ARBITRAGEUR_SYS', 'user_message': 'examples.GamblerFallacy.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GamblerFallacy.RuleLLM.prompts:RULELLM_ARBITRAGEUR_SYS', 'user_message': 'examples.GamblerFallacy.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GamblerFallacy.Rag.prompts:RAGLLM_ARBITRAGEUR_SYS', 'user_message': 'examples.GamblerFallacy.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `3000` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | arbitrageur | Arbitrageur | `Arbitrageur` | 1 | `examples/GamblerFallacy/Rule/players.py` |
| LLM | arbitrageur | Arbitrageur | `LLMArbitrageur` | 1 | `examples/GamblerFallacy/LLM/players.py` |
| RuleLLM | arbitrageur | Arbitrageur | `RuleLLMArbitrageur` | 1 | `examples/GamblerFallacy/RuleLLM/players.py` |
| Rag | arbitrageur | Arbitrageur | `RagLLMArbitrageur` | 1 | `examples/GamblerFallacy/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 Arbitrageur

**Summary**: Explicitly targets streak-based mispricing for profit. Functionally identical to IndependentAssessor in decision logic but conceptually represents a dedicated arbitrage strategy rather than passive fundamental investing. Together Section 4.3 and Section 4.4 constitute the rational stabilizing force whose combined capacity determines how quickly fallacy-driven deviations correct.

**Theoretical and Empirical Basis**: Shleifer & Vishny (1997) limits to arbitrage; De Long et al. (1990) noise trader risk; Pontiff (2006) arbitrage-cost evidence.

**Design Purpose**: Tests whether a dedicated mispricing exploiter can offset biased streak traders without erasing the phenomenon completely.

**Behavioral Framework**: Uses `configs/GamblerFallacy/Rule/players.yml -> arbitrageur.config.extras.activation_threshold`, `quantity_scale`, and `max_order`; these match the IndependentAssessor scale so both rational agents form a capacity-limited correction force.

**Decision Process**:
1. Hold while mispricing is small.
2. Buy when price is sufficiently below fundamental.
3. Sell when price is sufficiently above fundamental.
4. Cap order size by arbitrage capital and inventory constraints.

**Worked Numerical Example**: With `deviation = 0.07`, `activation_threshold = 0.05`, `quantity_scale = 3000`, and `max_order = 500`, desired quantity is 210; the arbitrageur sells 210 shares if available.

**Academic References**: Shleifer & Vishny (1997), De Long et al. (1990), Pontiff (2006). See Section 2.3.

## Source Docstring Excerpts

### Rule / `Arbitrageur`

```text
Theory: simulation-bases.md Section 4.4 -- Arbitrageur

Theoretical basis: Limits to arbitrage (Shleifer & Vishny, 1997).
Exploits mispricing caused by streak-based traders.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMArbitrageur`

```text
LLM-driven Arbitrageur: exploits mispricing caused by streak-based traders. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMArbitrageur`

```text
RuleLLM-driven Arbitrageur: exploits mispricing from streak-based traders. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMArbitrageur`

```text
RagLLM-driven arbitrageur: exploits gambler's fallacy mispricing. Theory: simulation-bases.md Section 4.4.
```
