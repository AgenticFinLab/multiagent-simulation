# Volmageddon / Vol ETN Manager

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | Volmageddon |
| Agent type | Vol ETN Manager |
| Canonical class | `VolETNManager` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A mechanical inverse-volatility product manager whose rebalancing creates procyclical volatility demand.

## Financial Theory / Theoretical Basis

### Rule / `VolETNManager`
- Theory: simulation-bases.md Section 4.2

### LLM / `LLMVolETNManager`
- Theory: simulation-bases.md Section 4.2

### RuleLLM / `RuleLLMVolETNManager`
- Theory: simulation-bases.md Section 4.2

### Rag / `RagLLMVolETNManager`
- Theory: simulation-bases.md Section 4.2

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| agent_type | LLM: `vol_e_t_n_manager`<br>RuleLLM: `vol_e_t_n_manager`<br>Rag: `vol_e_t_n_manager` | LLM, Rag, RuleLLM |
| fundamental_value | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | LLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>RuleLLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>Rag: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| rebalance_size | Rule: `10000` | Rule |
| rebalance_threshold | Rule: `0.05` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | vol_e_t_n_manager_2 | VolETNManager 2 | `VolETNManager` | 2 | `examples/Volmageddon/Rule/players.py` |
| LLM | vol_e_t_n_manager_2 | VolETNManager 2 | `LLMVolETNManager` | 2 | `examples/Volmageddon/LLM/players.py` |
| RuleLLM | vol_e_t_n_manager_2 | VolETNManager 2 | `RuleLLMVolETNManager` | 2 | `examples/Volmageddon/RuleLLM/players.py` |
| Rag | vol_e_t_n_manager_2 | VolETNManager 2 | `RagLLMVolETNManager` | 2 | `examples/Volmageddon/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 VolETNManager

**Summary**: A mechanical inverse-volatility product manager whose rebalancing
creates procyclical volatility demand.

**Theoretical and Empirical Basis**: Inverse-volatility ETPs reduce inverse
exposure after volatility rises by buying volatility-linked futures or
equivalent exposure. The 2018 XIV event is the historical anchor.

**Design Purpose**: Encode the central Volmageddon feedback channel: higher
volatility forces buying, and that buying can push the volatility proxy higher.

**Behavioral Framework**: Reads `rebalance_threshold` and `rebalance_size` from
`players.yml`; buying activates when positive deviation crosses the threshold.

**Decision Process**: If `deviation > rebalance_threshold`, buy
`int(deviation * rebalance_size)` units subject to current cash. Otherwise hold.

**Worked Numerical Example**: With `rebalance_threshold = 0.05`,
`rebalance_size = 10000`, and deviation `0.12`, the target order before cash
constraints is `int(0.12 * 10000) = 1200` buy units.

**Academic References**: Volatility product feedback is grounded in inverse-VIX
ETP disclosures, exchange event studies, and the limits-to-arbitrage literature.

## Source Docstring Excerpts

### Rule / `VolETNManager`

```text
Inverse VIX ETN manager.

Theory: simulation-bases.md Section 4.2
```

### LLM / `LLMVolETNManager`

```text
LLM-driven inverse VIX ETN manager.

Theory: simulation-bases.md Section 4.2
```

### RuleLLM / `RuleLLMVolETNManager`

```text
RuleLLM-driven inverse VIX ETN manager.

Theory: simulation-bases.md Section 4.2
```

### Rag / `RagLLMVolETNManager`

```text
RAG-augmented inverse VIX ETN manager.

Theory: simulation-bases.md Section 4.2
```
