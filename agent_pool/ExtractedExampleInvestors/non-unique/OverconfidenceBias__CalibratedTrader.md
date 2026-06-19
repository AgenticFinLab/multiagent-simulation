# OverconfidenceBias / Calibrated Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | OverconfidenceBias |
| Agent type | Calibrated Trader |
| Canonical class | `CalibratedTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

1. **Summary**: CalibratedTrader estimates signal precision correctly and trades only when the deviation is meaningful. It is the rational benchmark. 2. **Theoretical and Empirical Foundation**: Grossman and Stiglitz (1980, DOI `10.2307/1805228`) motivate disciplined information-based trading. 3. **Design Purpose and Activation Scenarios**: Activates only when `abs(deviation) > trade_threshold`. 4. **Behavioral Framework**: Trades in the value direction: buy undervaluation and sell overvaluation. Quantity scales with `signal_precision`. 5. **Decision Process Walkthrough**: Compare price to fundamental, verify the threshold, compute bounded size, and emit a stabilizing order. 6. **Worked Numerical Example**: If price is 4% below fundamental and threshold is 3%, it buys a bounded quantity proportional to signal precision. 7. **Academic References**: Grossman and Stiglitz (1980), Odean (1998).

## Financial Theory / Theoretical Basis

### Rule / `CalibratedTrader`
- Theoretical basis: simulation-bases.md Section 4.3 -- CalibratedTrader.

### LLM / `LLMCalibratedTrader`
- Theoretical basis: simulation-bases.md Section 4.3 -- CalibratedTrader.

### RuleLLM / `RuleLLMCalibratedTrader`
- Theoretical basis: simulation-bases.md Section 4.3 -- CalibratedTrader.

### Rag / `RagLLMCalibratedTrader`
- Theoretical basis: simulation-bases.md Section 4.3 -- CalibratedTrader.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.OverconfidenceBias.LLM.prompts:LLM_CALIBRATED_TRADER_PROMPT', 'user_message': 'examples.OverconfidenceBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.OverconfidenceBias.RuleLLM.prompts:RULELLM_CALIBRATED_TRADER_SYS', 'user_message': 'examples.OverconfidenceBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.OverconfidenceBias.Rag.prompts:RULELLM_CALIBRATED_TRADER_SYS', 'user_message': 'examples.OverconfidenceBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| signal_precision | Rule: `1.0` | Rule |
| trade_threshold | Rule: `0.03`<br>LLM: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | calibratedtrader | CalibratedTrader | `CalibratedTrader` | 1 | `examples/OverconfidenceBias/Rule/players.py` |
| LLM | calibratedtrader | CalibratedTrader | `LLMCalibratedTrader` | 1 | `examples/OverconfidenceBias/LLM/players.py` |
| RuleLLM | calibratedtrader | CalibratedTrader | `RuleLLMCalibratedTrader` | 1 | `examples/OverconfidenceBias/RuleLLM/players.py` |
| Rag | calibratedtrader | CalibratedTrader | `RagLLMCalibratedTrader` | 1 | `examples/OverconfidenceBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 CalibratedTrader

1. **Summary**: CalibratedTrader estimates signal precision correctly and trades
only when the deviation is meaningful. It is the rational benchmark.
2. **Theoretical and Empirical Foundation**: Grossman and Stiglitz (1980, DOI
`10.2307/1805228`) motivate disciplined information-based trading.
3. **Design Purpose and Activation Scenarios**: Activates only when
`abs(deviation) > trade_threshold`.
4. **Behavioral Framework**: Trades in the value direction: buy undervaluation
and sell overvaluation. Quantity scales with `signal_precision`.
5. **Decision Process Walkthrough**: Compare price to fundamental, verify the
threshold, compute bounded size, and emit a stabilizing order.
6. **Worked Numerical Example**: If price is 4% below fundamental and threshold
is 3%, it buys a bounded quantity proportional to signal precision.
7. **Academic References**: Grossman and Stiglitz (1980), Odean (1998).

## Source Docstring Excerpts

### Rule / `CalibratedTrader`

```text
Correctly estimates signal precision, trades appropriately.

Theoretical basis: simulation-bases.md Section 4.3 -- CalibratedTrader.
Strategy specification: simulation-bases.md Section 4.3.4.
```

### LLM / `LLMCalibratedTrader`

```text
LLM-driven CalibratedTrader.

Theoretical basis: simulation-bases.md Section 4.3 -- CalibratedTrader.
Strategy specification: simulation-bases.md Section 4.3.4.
```

### RuleLLM / `RuleLLMCalibratedTrader`

```text
Hybrid: CalibratedTrader rules + LLM reasoning.

Theoretical basis: simulation-bases.md Section 4.3 -- CalibratedTrader.
Strategy specification: simulation-bases.md Section 4.3.4.
```

### Rag / `RagLLMCalibratedTrader`

```text
RAG-augmented CalibratedTrader.

Theoretical basis: simulation-bases.md Section 4.3 -- CalibratedTrader.
Strategy specification: simulation-bases.md Section 4.3.4.
```
