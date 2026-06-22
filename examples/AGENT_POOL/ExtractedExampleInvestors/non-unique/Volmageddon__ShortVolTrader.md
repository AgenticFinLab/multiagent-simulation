# Volmageddon / Short Vol Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | Volmageddon |
| Agent type | Short Vol Trader |
| Canonical class | `ShortVolTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A carry trader that sells volatility when the proxy is below fair value and covers short exposure when volatility rises sharply.

## Financial Theory / Theoretical Basis

### Rule / `ShortVolTrader`
- Theory: simulation-bases.md Section 4.1

### LLM / `LLMShortVolTrader`
- Theory: simulation-bases.md Section 4.1

### RuleLLM / `RuleLLMShortVolTrader`
- Theory: simulation-bases.md Section 4.1

### Rag / `RagLLMShortVolTrader`
- Theory: simulation-bases.md Section 4.1

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| agent_type | LLM: `short_vol_trader`<br>RuleLLM: `short_vol_trader`<br>Rag: `short_vol_trader` | LLM, Rag, RuleLLM |
| fundamental_value | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | LLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>RuleLLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>Rag: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| stop_loss | Rule: `0.15` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | short_vol_trader_1 | ShortVolTrader 1 | `ShortVolTrader` | 2 | `examples/Volmageddon/Rule/players.py` |
| LLM | short_vol_trader_1 | ShortVolTrader 1 | `LLMShortVolTrader` | 2 | `examples/Volmageddon/LLM/players.py` |
| RuleLLM | short_vol_trader_1 | ShortVolTrader 1 | `RuleLLMShortVolTrader` | 2 | `examples/Volmageddon/RuleLLM/players.py` |
| Rag | short_vol_trader_1 | ShortVolTrader 1 | `RagLLMShortVolTrader` | 2 | `examples/Volmageddon/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 ShortVolTrader

**Summary**: A carry trader that sells volatility when the proxy is below fair
value and covers short exposure when volatility rises sharply.

**Theoretical and Empirical Basis**: Short-volatility risk-premium strategies
earn roll/carry in calm periods but face asymmetric losses in volatility jumps.
The 2018 inverse-volatility collapse showed how crowded short-volatility
exposure can unwind abruptly.

**Design Purpose**: Provide destabilizing buy pressure during volatility spikes
through stop-loss covering, while supplying volatility exposure in calm periods.

**Behavioral Framework**: Reads `stop_loss` from `players.yml`; positive
deviation above this threshold triggers buy-to-cover pressure, while negative
deviation below -2% triggers additional short-volatility selling.

**Decision Process**: If `deviation > stop_loss` and the agent is short, buy up
to 80% of absolute short position. If `deviation < -0.02`, sell up to 1,000
units subject to available cash and current proxy price. Otherwise hold.

**Worked Numerical Example**: With `stop_loss = 0.15`, a move from 15.00 to
18.00 gives deviation `(18 - 15) / 15 = 0.20`; a trader short 1,000 units buys
up to 800 units to cover.

**Academic References**: Volatility clustering and risk-premium logic follows
Engle (1982), Bollerslev (1986), and volatility-managed exposure literature.

## Source Docstring Excerpts

### Rule / `ShortVolTrader`

```text
Short volatility trader.

Theory: simulation-bases.md Section 4.1
```

### LLM / `LLMShortVolTrader`

```text
LLM-driven short volatility trader.

Theory: simulation-bases.md Section 4.1
```

### RuleLLM / `RuleLLMShortVolTrader`

```text
RuleLLM-driven short volatility trader.

Theory: simulation-bases.md Section 4.1
```

### Rag / `RagLLMShortVolTrader`

```text
RAG-augmented short volatility trader.

Theory: simulation-bases.md Section 4.1
```
