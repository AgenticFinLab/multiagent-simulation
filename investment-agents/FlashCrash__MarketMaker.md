# FlashCrash / Market Maker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash |
| Agent type | Market Maker |
| Canonical class | `MarketMaker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, RuleLLM, Rag |

## Definition and Goal

**Role:** Liquidity provider that withdraws under stress; key amplification mechanism.

## Financial Theory / Theoretical Basis

### Rule / `MarketMaker`
- Theory: simulation-bases.md Section 4.2 -- MarketMaker
- Theoretical basis: Grossman & Miller (1988) liquidity provider model;

### RuleLLM / `RuleLLMMarketMaker`
- Hybrid: Liquidity provision + withdrawal rules + LLM risk reasoning. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMMarketMaker`
- RAG-augmented market maker -- liquidity provision/withdrawal rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_liquidity | Rule: `30.0`<br>RuleLLM: `30.0`<br>Rag: `30.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>RuleLLM: `3`<br>Rag: `3` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | Rag, Rule, RuleLLM |
| llm | RuleLLM: `{'sys_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_MARKET_MAKER_SYS', 'user_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_MARKET_MAKER_SYS', 'user_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| spread_sensitivity | Rule: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | Rag, Rule, RuleLLM |
| volatility_threshold | Rule: `0.02`<br>RuleLLM: `0.02`<br>Rag: `0.02` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | market_maker | Market Maker | `MarketMaker` | 3 | `examples/FlashCrash/Rule/players.py` |
| RuleLLM | rulellm_market_maker | RuleLLM Market Maker | `RuleLLMMarketMaker` | 3 | `examples/FlashCrash/RuleLLM/players.py` |
| Rag | ragllm_market_maker | RAG Market Maker | `RagLLMMarketMaker` | 3 | `examples/FlashCrash/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 MarketMaker

**Role:** Liquidity provider that withdraws under stress; key amplification mechanism.

**Behavioural model:**
```python
price_return = abs((price - prev_price) / prev_price)
if price_return > volatility_threshold:
    provides_liquidity = False
    quantity = -position * 0.3        # sell 30 % of inventory
else:
    provides_liquidity = True
    quantity = -position * 0.2        # rebalance toward zero inventory
```

**Parameters:** `volatility_threshold`, `base_position_size`

**Decision rule:** Provides liquidity and rebalances inventory in calm conditions; withdraws and partially liquidates when single-round return exceeds `volatility_threshold`.

**Market effect:** Withdrawal reduces `total_liquidity`, raises `liquidity_factor`, amplifying all subsequent orders.

**Theory:** Grossman & Miller (1988); Kirilenko et al. (2017) -- liquidity vacuum mechanism.

**Diversity:** Varied `volatility_threshold` (0.005-0.02) -- some pull back earlier than others.

**Distinguishing feature:** The only agent whose `provides_liquidity` flag toggles; the sole driver of the liquidity multiplier.

---

## Source Docstring Excerpts

### Rule / `MarketMaker`

```text
Market maker providing liquidity, withdraws in stress.

Theory: simulation-bases.md Section 4.2 -- MarketMaker
Theoretical basis: Grossman & Miller (1988) liquidity provider model;
stress-induced withdrawal creates a liquidity vacuum amplifying the crash.
See simulation-bases.md Section 4.2 for mathematical model.

Parameters from config extras:
    - volatility_threshold, base_liquidity, spread_sensitivity
```

### RuleLLM / `RuleLLMMarketMaker`

```text
Hybrid: Liquidity provision + withdrawal rules + LLM risk reasoning. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMMarketMaker`

```text
RAG-augmented market maker -- liquidity provision/withdrawal rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.2.
```
