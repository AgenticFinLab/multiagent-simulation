# StatusQuoBias / Momentum Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | StatusQuoBias |
| Agent type | Momentum Trader |
| Canonical class | `MomentumTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor represents trend followers who react to visible price movement rather than default allocations.

## Financial Theory / Theoretical Basis

### Rule / `MomentumTrader`
- Theory: simulation-bases.md Section 4.4 -- MomentumTrader
- Theoretical basis: momentum-based trading.

### LLM / `LLMMomentumTrader`
- LLM-driven momentum trader naturally overcoming status quo. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMMomentumTrader`
- RuleLLM momentum trader naturally overcoming status quo. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMMomentumTrader`
- RagLLM momentum trader naturally overcoming status quo. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| entry_threshold | Rule: `0.01`<br>LLM: `0.01`<br>RuleLLM: `0.01`<br>Rag: `0.01` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.StatusQuoBias.LLM.prompts:LLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.StatusQuoBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.StatusQuoBias.Rag.prompts:RAGLLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.StatusQuoBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentumtrader | MomentumTrader | `MomentumTrader` | 2 | `examples/StatusQuoBias/Rule/players.py` |
| LLM | momentumtrader | MomentumTrader | `LLMMomentumTrader` | 2 | `examples/StatusQuoBias/LLM/players.py` |
| RuleLLM | momentumtrader | MomentumTrader | `RuleLLMMomentumTrader` | 2 | `examples/StatusQuoBias/RuleLLM/players.py` |
| Rag | momentumtrader | MomentumTrader | `RagLLMMomentumTrader` | 2 | `examples/StatusQuoBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 MomentumTrader

#### Section 4.4.1 Summary

This investor represents trend followers who react to visible price movement
rather than default allocations.

It offsets pure inaction and can temporarily amplify mispricing by buying into
positive deviations or selling into negative deviations.

#### Section 4.4.2 Theoretical and Empirical Foundation

Jegadeesh and Titman (1993) document intermediate-horizon momentum returns. The
simulation uses deviation direction as the observable trend proxy.

#### Section 4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation > entry_threshold` | Buy | Reinforces upward trend | Section 2.5 |
| `deviation < -entry_threshold` | Sell | Reinforces downward trend | Section 2.5 |
| Weak trend | Hold | Avoids excessive churn | Section 2.5 |

#### Section 4.4.4 Behavioral Framework

The agent uses `entry_threshold` and `position_size`. It follows deviation sign
as a compact proxy for trend pressure in this scenario.

#### Section 4.4.5 Decision Process Walkthrough

A 2% positive deviation with `entry_threshold=1%` triggers buying. A 0.5%
positive deviation does not.

#### Section 4.4.6 Worked Numerical Example

```text
P=102, F=100, delta=0.02, entry_threshold=0.01
Q = 300 * 0.02 / 0.01 = 600 shares, capped by cash
```

#### Section 4.4.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Jegadeesh and Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Momentum trading pressure. |
| 2 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x | Contrast with noise-driven orders. |

## Source Docstring Excerpts

### Rule / `MomentumTrader`

```text
Trades on price trends, naturally overcoming status quo inertia.

Theory: simulation-bases.md Section 4.4 -- MomentumTrader
Theoretical basis: momentum-based trading.
See simulation-bases.md Section 4.4 for mathematical model.

Parameters from config extras:
    - lookback, entry_threshold
```

### LLM / `LLMMomentumTrader`

```text
LLM-driven momentum trader naturally overcoming status quo. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMMomentumTrader`

```text
RuleLLM momentum trader naturally overcoming status quo. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMMomentumTrader`

```text
RagLLM momentum trader naturally overcoming status quo. Theory: simulation-bases.md Section 4.4.
```
