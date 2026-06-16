# MarketCrash / Market Maker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MarketCrash |
| Agent type | Market Maker |
| Canonical class | `MarketMaker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A liquidity supplier that withdraws under stress. **Theoretical and Empirical Basis**: Liquidity suppliers require compensation for immediacy and inventory risk; see Grossman and Miller (1988, DOI: 10.1111/j.1540-6261.1988.tb04594.x). **Design Purpose**: Make crash severity depend on endogenous market depth. **Behavioral Framework**: Uses volatility withdrawal threshold, inventory limits, quote size, and spread multiplier. **Decision Process**: Provide stabilizing quotes in normal markets; reduce quantity when volatility exceeds threshold or inventory risk is high. **Worked Numerical Example**: If normal quote size is 20 but volatility exceeds the withdrawal threshold, the submitted liquidity quantity shrinks or turns to defensive inventory reduction. **Academic References**: Grossman and Miller (1988); Brunnermeier and Pedersen (2009).

## Financial Theory / Theoretical Basis

### Rule / `MarketMaker`
- Theory: simulation-bases.md Section 4.3.

### LLM / `LLMMarketMaker`
- LLM MarketMaker. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMMarketMaker`
- Hybrid MarketMaker. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMMarketMaker`
- RAG MarketMaker. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `30.0`<br>RuleLLM: `30.0`<br>Rag: `30.0` | LLM, Rag, Rule, RuleLLM |
| inventory_limit | Rule: `30.0` | Rule |
| llm | LLM: `{'sys_message': 'examples.MarketCrash.LLM.prompts:LLM_MARKET_MAKER_SYS', 'user_message': 'examples.MarketCrash.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_MARKET_MAKER_SYS', 'user_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_MARKET_MAKER_SYS', 'user_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| normal_quote_size | Rule: `20.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| spread_multiplier | Rule: `0.02` | Rule |
| volatility_withdraw_threshold | Rule: `5.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | market_maker | Market Maker | `MarketMaker` | 2 | `examples/MarketCrash/Rule/players.py` |
| LLM | llm_market_maker | LLM Market Maker | `LLMMarketMaker` | 2 | `examples/MarketCrash/LLM/players.py` |
| RuleLLM | rulellm_market_maker | RuleLLM Market Maker | `RuleLLMMarketMaker` | 2 | `examples/MarketCrash/RuleLLM/players.py` |
| Rag | ragllm_market_maker | RAG Market Maker | `RagLLMMarketMaker` | 2 | `examples/MarketCrash/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 MarketMaker

**Summary**: A liquidity supplier that withdraws under stress.
**Theoretical and Empirical Basis**: Liquidity suppliers require compensation
for immediacy and inventory risk; see Grossman and Miller (1988, DOI:
10.1111/j.1540-6261.1988.tb04594.x).
**Design Purpose**: Make crash severity depend on endogenous market depth.
**Behavioral Framework**: Uses volatility withdrawal threshold, inventory
limits, quote size, and spread multiplier.
**Decision Process**: Provide stabilizing quotes in normal markets; reduce
quantity when volatility exceeds threshold or inventory risk is high.
**Worked Numerical Example**: If normal quote size is 20 but volatility exceeds
the withdrawal threshold, the submitted liquidity quantity shrinks or turns to
defensive inventory reduction.
**Academic References**: Grossman and Miller (1988); Brunnermeier and Pedersen
(2009).

## Source Docstring Excerpts

### Rule / `MarketMaker`

```text
Market maker providing liquidity (and withdrawing in stress).

Theory: simulation-bases.md Section 4.3.

Parameters from config extras:
    - volatility_withdraw_threshold, inventory_limit, normal_quote_size, spread_multiplier
```

### LLM / `LLMMarketMaker`

```text
LLM MarketMaker. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMMarketMaker`

```text
Hybrid MarketMaker. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMMarketMaker`

```text
RAG MarketMaker. Theory: simulation-bases.md Section 4.3.
```
