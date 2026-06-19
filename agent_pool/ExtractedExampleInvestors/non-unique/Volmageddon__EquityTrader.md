# Volmageddon / Equity Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | Volmageddon |
| Agent type | Equity Trader |
| Canonical class | `EquityTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: An equity-market participant that de-risks when volatility stress breaches risk limits and buys when prices are deeply below fundamental value.

## Financial Theory / Theoretical Basis

### Rule / `EquityTrader`
- Theory: simulation-bases.md Section 4.5

### LLM / `LLMEquityTrader`
- Theory: simulation-bases.md Section 4.5

### RuleLLM / `RuleLLMEquityTrader`
- Theory: simulation-bases.md Section 4.5

### Rag / `RagLLMEquityTrader`
- Theory: simulation-bases.md Section 4.5

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| agent_type | LLM: `equity_trader`<br>RuleLLM: `equity_trader`<br>Rag: `equity_trader` | LLM, Rag, RuleLLM |
| fundamental_value | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `15.0`<br>LLM: `15.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | LLM, Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | LLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>RuleLLM: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}`<br>Rag: `{'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| risk_limit | Rule: `0.1` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | equity_trader_5 | EquityTrader 5 | `EquityTrader` | 2 | `examples/Volmageddon/Rule/players.py` |
| LLM | equity_trader_5 | EquityTrader 5 | `LLMEquityTrader` | 2 | `examples/Volmageddon/LLM/players.py` |
| RuleLLM | equity_trader_5 | EquityTrader 5 | `RuleLLMEquityTrader` | 2 | `examples/Volmageddon/RuleLLM/players.py` |
| Rag | equity_trader_5 | EquityTrader 5 | `RagLLMEquityTrader` | 2 | `examples/Volmageddon/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 EquityTrader

**Summary**: An equity-market participant that de-risks when volatility stress
breaches risk limits and buys when prices are deeply below fundamental value.

**Theoretical and Empirical Basis**: Volatility targeting, risk parity, and
risk-control strategies reduce exposure in high-volatility regimes.

**Design Purpose**: Connect the volatility-product shock to broader equity
market selling pressure.

**Behavioral Framework**: Reads `risk_limit`; action activates only when
`abs(deviation) > 2 * risk_limit`.

**Decision Process**: If the proxy is sharply below fundamental, buy up to a
deviation-scaled quantity. If the proxy is sharply above fundamental, sell down
risk subject to current position. Otherwise hold.

**Worked Numerical Example**: With `risk_limit = 0.1`, a deviation of 0.25
exceeds the 0.20 activation threshold; a trader with inventory sells up to
`min(1000, int(0.25 * 3000)) = 750` units.

**Academic References**: The role follows volatility-managed exposure evidence
(Moreira and Muir, 2017) and liquidity feedback theory (Brunnermeier and
Pedersen, 2009).

## Source Docstring Excerpts

### Rule / `EquityTrader`

```text
Equity trader.

Theory: simulation-bases.md Section 4.5
```

### LLM / `LLMEquityTrader`

```text
LLM-driven equity trader.

Theory: simulation-bases.md Section 4.5
```

### RuleLLM / `RuleLLMEquityTrader`

```text
RuleLLM-driven equity trader.

Theory: simulation-bases.md Section 4.5
```

### Rag / `RagLLMEquityTrader`

```text
RAG-augmented equity trader.

Theory: simulation-bases.md Section 4.5
```
