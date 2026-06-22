# Volmageddon / Vol Arbitrageur

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | Volmageddon |
| Agent type | Vol Arbitrageur |
| Canonical class | `VolArbitrageur` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A model-based arbitrageur that trades large volatility proxy dislocations toward fundamental value.

## Financial Theory / Theoretical Basis

### Rule / `VolArbitrageur`
- Theory: simulation-bases.md Section 4.4

### LLM / `LLMVolArbitrageur`
- Theory: simulation-bases.md Section 4.4

### RuleLLM / `RuleLLMVolArbitrageur`
- Theory: simulation-bases.md Section 4.4

### Rag / `RagLLMVolArbitrageur`
- Theory: simulation-bases.md Section 4.4

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| agent_type | LLM: `vol_arbitrageur`<br>RuleLLM: `vol_arbitrageur`<br>Rag: `vol_arbitrageur` | LLM, Rag, RuleLLM |
| entry_threshold | Rule: `0.05` | Rule |
| fundamental_value | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | LLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>RuleLLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>Rag: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | vol_arbitrageur_4 | VolArbitrageur 4 | `VolArbitrageur` | 2 | `examples/Volmageddon/Rule/players.py` |
| LLM | vol_arbitrageur_4 | VolArbitrageur 4 | `LLMVolArbitrageur` | 2 | `examples/Volmageddon/LLM/players.py` |
| RuleLLM | vol_arbitrageur_4 | VolArbitrageur 4 | `RuleLLMVolArbitrageur` | 2 | `examples/Volmageddon/RuleLLM/players.py` |
| Rag | vol_arbitrageur_4 | VolArbitrageur 4 | `RagLLMVolArbitrageur` | 2 | `examples/Volmageddon/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 VolArbitrageur

**Summary**: A model-based arbitrageur that trades large volatility proxy
dislocations toward fundamental value.

**Theoretical and Empirical Basis**: Volatility arbitrage exploits differences
between implied, realized, and fundamental volatility, but capital and risk
limits can prevent immediate convergence.

**Design Purpose**: Add partial stabilizing pressure without assuming unlimited
arbitrage capital.

**Behavioral Framework**: Reads `entry_threshold`; only deviations with absolute
magnitude above the threshold trigger orders.

**Decision Process**: If `abs(deviation) > entry_threshold`, compute
`min(5000, int(abs(deviation) * 20000))`; sell when volatility is expensive and
buy when it is cheap, subject to position and cash limits.

**Worked Numerical Example**: With `entry_threshold = 0.05` and deviation 0.18,
the raw target is `int(0.18 * 20000) = 3600`; the arbitrageur sells up to 3,600
units if it has sufficient long inventory.

**Academic References**: The design follows limits-to-arbitrage theory
(Shleifer and Vishny, 1997) and volatility term-structure arbitrage practice.

## Source Docstring Excerpts

### Rule / `VolArbitrageur`

```text
Volatility arbitrageur.

Theory: simulation-bases.md Section 4.4
```

### LLM / `LLMVolArbitrageur`

```text
LLM-driven volatility arbitrageur.

Theory: simulation-bases.md Section 4.4
```

### RuleLLM / `RuleLLMVolArbitrageur`

```text
RuleLLM-driven volatility arbitrageur.

Theory: simulation-bases.md Section 4.4
```

### Rag / `RagLLMVolArbitrageur`

```text
RAG-augmented volatility arbitrageur.

Theory: simulation-bases.md Section 4.4
```
