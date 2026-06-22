# FlashCrash2010 / Fundamental Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash2010 |
| Agent type | Fundamental Trader |
| Canonical class | `FundamentalTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Role:** Value-based contrarian; stabilising and recovery force.

## Financial Theory / Theoretical Basis

### Rule / `FundamentalTrader`
- Theory: simulation-bases.md Section 4.3 -- FundamentalTrader
- Theoretical basis: Shiller (1981) excess volatility; fundamental traders

### LLM / `LLMFundamentalTrader`
- LLM-driven fundamental trader -- value-based stabilization via LLM analytical reasoning. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMFundamentalTrader`
- Hybrid: Value deviation rules + LLM analytical reasoning. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMFundamentalTrader`
- RAG-augmented fundamental trader -- value deviation rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FlashCrash2010.LLM.prompts:LLM_FUNDAMENTAL_SYS', 'user_message': 'examples.FlashCrash2010.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_FUNDAMENTAL_SYS', 'user_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FlashCrash2010.Rag.prompts:RAGLLM_FUNDAMENTAL_SYS', 'user_message': 'examples.FlashCrash2010.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| value_trigger | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | fundamentaltrader | FundamentalTrader | `FundamentalTrader` | 2 | `examples/FlashCrash2010/Rule/players.py` |
| LLM | fundamentaltrader | FundamentalTrader | `LLMFundamentalTrader` | 2 | `examples/FlashCrash2010/LLM/players.py` |
| RuleLLM | fundamentaltrader | FundamentalTrader | `RuleLLMFundamentalTrader` | 2 | `examples/FlashCrash2010/RuleLLM/players.py` |
| Rag | fundamentaltrader | FundamentalTrader | `RagLLMFundamentalTrader` | 2 | `examples/FlashCrash2010/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 FundamentalTrader

**Role:** Value-based contrarian; stabilising and recovery force.

**Behavioural model:**
```python
deviation = (price - fundamental) / fundamental
if deviation < -value_trigger:
    quantity = min(order_size, int(cash / price))   # buy undervalued
elif deviation > value_trigger:
    quantity = -min(order_size, position)            # sell overvalued
else:
    quantity = 0
provides_liquidity: True
agent_type: "fundamental"
```

**Parameters:** `value_trigger`, `order_size`

**Decision rule:** Buys (sells) when price deviates more than `value_trigger` below (above) fundamental; fixed order size.

**Market effect:** Absorbs sell pressure at the trough; drives price recovery toward fundamental.

**Theory:** Shiller (1981) -- excess volatility correction; fundamental value gravity.

**Diversity:** Varied `value_trigger` (0.03-0.10) and `order_size` (200-1000) across instances.

**Distinguishing feature:** `provides_liquidity: True` and `agent_type = "fundamental"` -- does not count toward HFT participation; provides stabilising force.

---

## Source Docstring Excerpts

### Rule / `FundamentalTrader`

```text
Value-based fundamental trader - stabilizing force.

Theory: simulation-bases.md Section 4.3 -- FundamentalTrader
Theoretical basis: Shiller (1981) excess volatility; fundamental traders
recognize undervaluation and buy aggressively, providing the recovery force.
See simulation-bases.md Section 4.3 for mathematical model.

Parameters from config extras:
    - initial_cash, initial_position, value_trigger, order_size,
      custom_state_hot_limit, record_path
```

### LLM / `LLMFundamentalTrader`

```text
LLM-driven fundamental trader -- value-based stabilization via LLM analytical reasoning. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMFundamentalTrader`

```text
Hybrid: Value deviation rules + LLM analytical reasoning. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMFundamentalTrader`

```text
RAG-augmented fundamental trader -- value deviation rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.3.
```
