# GamblerFallacy / Independent Assessor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GamblerFallacy |
| Agent type | Independent Assessor |
| Canonical class | `IndependentAssessor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Represents quantitative traders or statistically trained investors who correctly treat each price change as independent (no streak fallacy). They trade contrarian to the current deviation -- buying when price is below fundamental (deviation < -0.05) and selling when above (deviation > 0.05). Their 5% threshold and 500-share cap reflect both a higher evidence bar for independent-evidence reasoning and the limits to arbitrage constraints.

## Financial Theory / Theoretical Basis

### Rule / `IndependentAssessor`
- Theory: simulation-bases.md Section 4.3 -- IndependentAssessor
- Theoretical basis: Independence of sequential events (Rabin, 2002 baseline).

### LLM / `LLMIndependentAssessor`
- LLM-driven IndependentAssessor: treats each price change as independent. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMIndependentAssessor`
- RuleLLM-driven IndependentAssessor: treats each price change as independent. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMIndependentAssessor`
- RagLLM-driven independent assessor: ignores streak patterns, trades on fundamentals. Theory: simulation-bases.md Section 4.3.

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
| llm | LLM: `{'sys_message': 'examples.GamblerFallacy.LLM.prompts:LLM_INDEPENDENT_ASSESSOR_SYS', 'user_message': 'examples.GamblerFallacy.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GamblerFallacy.RuleLLM.prompts:RULELLM_INDEPENDENT_ASSESSOR_SYS', 'user_message': 'examples.GamblerFallacy.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GamblerFallacy.Rag.prompts:RAGLLM_INDEPENDENT_ASSESSOR_SYS', 'user_message': 'examples.GamblerFallacy.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `3000` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | independentassessor | IndependentAssessor | `IndependentAssessor` | 1 | `examples/GamblerFallacy/Rule/players.py` |
| LLM | independentassessor | IndependentAssessor | `LLMIndependentAssessor` | 1 | `examples/GamblerFallacy/LLM/players.py` |
| RuleLLM | independentassessor | IndependentAssessor | `RuleLLMIndependentAssessor` | 1 | `examples/GamblerFallacy/RuleLLM/players.py` |
| Rag | independentassessor | IndependentAssessor | `RagLLMIndependentAssessor` | 1 | `examples/GamblerFallacy/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 IndependentAssessor

**Summary**: Represents quantitative traders or statistically trained investors who correctly treat each price change as independent (no streak fallacy). They trade contrarian to the current deviation -- buying when price is below fundamental (deviation < -0.05) and selling when above (deviation > 0.05). Their 5% threshold and 500-share cap reflect both a higher evidence bar for independent-evidence reasoning and the limits to arbitrage constraints.

**Theoretical and Empirical Basis**: Rabin (2002) rational benchmark; Shleifer & Vishny (1997) limits to arbitrage; De Bondt & Thaler (1985) long-horizon reversal.

**Design Purpose**: Provides the rational stabilizing population. It counters behavioral order flow only when mispricing is large enough to justify action, allowing biased pressure to remain visible.

**Behavioral Framework**: Reads `configs/GamblerFallacy/Rule/players.yml -> independentassessor.config.extras.activation_threshold`, `quantity_scale`, and `max_order`.

**Decision Process**:
1. Hold unless `abs(deviation) > activation_threshold`.
2. If `deviation < 0`, buy undervalued shares.
3. If `deviation > 0`, sell overvalued shares.
4. Cap quantity by `max_order`, cash, and holdings.

**Worked Numerical Example**: With `deviation = -0.08`, `activation_threshold = 0.05`, `quantity_scale = 3000`, and `max_order = 500`, desired quantity is `min(500, 240) = 240`; the assessor buys 240 shares if cash permits.

**Academic References**: Rabin (2002), Shleifer & Vishny (1997), De Bondt & Thaler (1985). See Section 2.3.

## Source Docstring Excerpts

### Rule / `IndependentAssessor`

```text
Theory: simulation-bases.md Section 4.3 -- IndependentAssessor

Theoretical basis: Independence of sequential events (Rabin, 2002 baseline).
Correctly treats each price change as independent, no streak bias.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMIndependentAssessor`

```text
LLM-driven IndependentAssessor: treats each price change as independent. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMIndependentAssessor`

```text
RuleLLM-driven IndependentAssessor: treats each price change as independent. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMIndependentAssessor`

```text
RagLLM-driven independent assessor: ignores streak patterns, trades on fundamentals. Theory: simulation-bases.md Section 4.3.
```
