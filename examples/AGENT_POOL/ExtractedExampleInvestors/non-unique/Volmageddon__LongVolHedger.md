# Volmageddon / Long Vol Hedger

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | Volmageddon |
| Agent type | Long Vol Hedger |
| Canonical class | `LongVolHedger` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A portfolio-insurance investor that owns volatility exposure as a hedge and can take profits after spikes.

## Financial Theory / Theoretical Basis

### Rule / `LongVolHedger`
- Theory: simulation-bases.md Section 4.3

### LLM / `LLMLongVolHedger`
- Theory: simulation-bases.md Section 4.3

### RuleLLM / `RuleLLMLongVolHedger`
- Theory: simulation-bases.md Section 4.3

### Rag / `RagLLMLongVolHedger`
- Theory: simulation-bases.md Section 4.3

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| agent_type | LLM: `long_vol_hedger`<br>RuleLLM: `long_vol_hedger`<br>Rag: `long_vol_hedger` | LLM, Rag, RuleLLM |
| fundamental_value | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| hedge_ratio | Rule: `0.1` | Rule |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | LLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>RuleLLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>Rag: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | long_vol_hedger_3 | LongVolHedger 3 | `LongVolHedger` | 1 | `examples/Volmageddon/Rule/players.py` |
| LLM | long_vol_hedger_3 | LongVolHedger 3 | `LLMLongVolHedger` | 1 | `examples/Volmageddon/LLM/players.py` |
| RuleLLM | long_vol_hedger_3 | LongVolHedger 3 | `RuleLLMLongVolHedger` | 1 | `examples/Volmageddon/RuleLLM/players.py` |
| Rag | long_vol_hedger_3 | LongVolHedger 3 | `RagLLMLongVolHedger` | 1 | `examples/Volmageddon/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 LongVolHedger

**Summary**: A portfolio-insurance investor that owns volatility exposure as a
hedge and can take profits after spikes.

**Theoretical and Empirical Basis**: Long-volatility hedges are costly in calm
markets but pay off during market stress. Volatility-managed portfolio theory
motivates state-dependent risk allocation.

**Design Purpose**: Provide a stabilizing role that can buy when volatility is
cheap and sell into spikes, offsetting part of the short-volatility unwind.

**Behavioral Framework**: Reads `hedge_ratio`; negative deviation below -5%
triggers hedge accumulation, and positive deviation above 10% triggers partial
profit-taking.

**Decision Process**: If volatility is cheap, buy up to 500 units scaled by cash
and `hedge_ratio`. If volatility is expensive and the agent has a long position,
sell up to 500 units. Otherwise hold.

**Worked Numerical Example**: With cash 1,000,000, price 14.00, and
`hedge_ratio = 0.1`, the raw hedge budget is 100,000; the scenario cap limits
the buy order to 500 units.

**Academic References**: The role follows crash-insurance intuition and the
volatility-managed portfolio evidence in Moreira and Muir (2017).

## Source Docstring Excerpts

### Rule / `LongVolHedger`

```text
Long volatility hedger.

Theory: simulation-bases.md Section 4.3
```

### LLM / `LLMLongVolHedger`

```text
LLM-driven long volatility hedger.

Theory: simulation-bases.md Section 4.3
```

### RuleLLM / `RuleLLMLongVolHedger`

```text
RuleLLM-driven long volatility hedger.

Theory: simulation-bases.md Section 4.3
```

### Rag / `RagLLMLongVolHedger`

```text
RAG-augmented long volatility hedger.

Theory: simulation-bases.md Section 4.3
```
