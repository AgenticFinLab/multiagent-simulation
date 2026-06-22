# LiquidityDryup / Market Maker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LiquidityDryup |
| Agent type | Market Maker |
| Canonical class | `MarketMaker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements the Grossman-Miller (1988) immediacy provider who earns the bid-ask spread in normal conditions but withdraws when inventory risk from high volatility exceeds their risk tolerance. Withdrawal triggers the liquidity spiral by reducing `total_liquidity` and amplifying price impact.

## Financial Theory / Theoretical Basis

### Rule / `MarketMaker`
- Theory: simulation-bases.md Section 4.1
- Foundation: Grossman & Miller (1988) doi:10.1111/j.1540-6261.1988.tb04594.x;
- Brunnermeier & Pedersen (2009) doi:10.1093/rfs/hhn098
- Formula: quantity = -position x withdraw_rebalance (stress); -position x normal_rebalance (normal)

### LLM / `LLMMarketMaker`
- Market maker - provides liquidity. Theory: simulation-bases.md Section 4.1

### RuleLLM / `RuleLLMMarketMaker`
- Hybrid: MarketMaker rules + LLM reasoning. Theory: simulation-bases.md Section 4.1

### Rag / `RagLLMMarketMaker`
- RAG-augmented: MarketMaker rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.1

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_liquidity | Rule: `30.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LiquidityDryup.LLM.prompts:LLM_MARKET_MAKER_SYS', 'user_message': 'examples.LiquidityDryup.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.LiquidityDryup.RuleLLM.prompts:RULELLM_MARKET_MAKER_SYS', 'user_message': 'examples.LiquidityDryup.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.LiquidityDryup.Rag.prompts:RAGLLM_MARKET_MAKER_SYS', 'user_message': 'examples.LiquidityDryup.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| normal_rebalance | Rule: `0.2` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| volatility_threshold | Rule: `0.02` | Rule |
| withdraw_rebalance | Rule: `0.3` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | market_maker | Market Maker | `MarketMaker` | 3 | `examples/LiquidityDryup/Rule/players.py` |
| LLM | llm_market_maker | LLM Market Maker | `LLMMarketMaker` | 3 | `examples/LiquidityDryup/LLM/players.py` |
| RuleLLM | rulellm_market_maker | RuleLLM Market Maker | `RuleLLMMarketMaker` | 3 | `examples/LiquidityDryup/RuleLLM/players.py` |
| Rag | ragllm_market_maker | RAG Market Maker | `RagLLMMarketMaker` | 3 | `examples/LiquidityDryup/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 MarketMaker

**Summary**: Implements the Grossman-Miller (1988) immediacy provider who earns the bid-ask spread in normal conditions but withdraws when inventory risk from high volatility exceeds their risk tolerance. Withdrawal triggers the liquidity spiral by reducing `total_liquidity` and amplifying price impact.

**Foundation**: Grossman, S. J., & Miller, M. H. (1988). doi:10.1111/j.1540-6261.1988.tb04594.x; Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:10.1093/rfs/hhn098

**Design Purpose**: Model the endogenous withdrawal of liquidity providers under stress. The critical threshold `volatility_threshold` represents the point where inventory risk dominates the spread revenue, replicating the empirically observed "liquidity vacuum" in stress episodes.

**Behavioral Framework**:

| Decision Variable | Logic                         | Formula                                                                        |
|-------------------|-------------------------------|--------------------------------------------------------------------------------|
| `volatility`      | Single-period absolute return | `abs(market_data["return"])`                                                   |
| Stress condition  | Exceed volatility threshold   | `volatility > volatility_threshold`                                            |
| Stress response   | Withdraw + offload inventory  | `provides_liquidity = 0; quantity = -position x withdraw_rebalance`            |
| Normal response   | Provide liquidity + rebalance | `provides_liquidity = base_liquidity; quantity = -position x normal_rebalance` |
| Quantity cap      | Risk management               | `max(-25, min(25, quantity))`                                                  |

**Decision Walkthrough**:
1. Receive market data: `{price, return, liquidity}`.
2. Compute `volatility = |return|`.
3. If `volatility > volatility_threshold`: set `provides_liquidity = 0`; sell/buy `position x withdraw_rebalance` shares to reduce inventory.
4. Else: set `provides_liquidity = base_liquidity`; rebalance inventory by `position x normal_rebalance`.
5. Cap quantity at ±25.

**Worked Example**: `position = 10`, `|return| = 0.04 > volatility_threshold = 0.02`. Withdraw: `provides_liquidity = 0`, `quantity = -10 x 0.3 = -3` (sell 3 to reduce inventory). Effective liquidity in market drops by `base_liquidity`, amplifying next-round price impact.

**References**: simulation-bases.md Section 2 Theory 1 (Grossman-Miller); doi:10.1111/j.1540-6261.1988.tb04594.x; doi:10.1093/rfs/hhn098

---

## Source Docstring Excerpts

### Rule / `MarketMaker`

```text
Market maker who provides liquidity but withdraws in stress.

Theory: simulation-bases.md Section 4.1
Foundation: Grossman & Miller (1988) doi:10.1111/j.1540-6261.1988.tb04594.x;
            Brunnermeier & Pedersen (2009) doi:10.1093/rfs/hhn098
Activation: |return| > volatility_threshold -> withdraw (provides_liquidity = 0)
Formula: quantity = -position x withdraw_rebalance (stress); -position x normal_rebalance (normal)

Parameters from config extras:
    - volatility_threshold, base_liquidity, withdraw_rebalance, normal_rebalance
```

### LLM / `LLMMarketMaker`

```text
Market maker - provides liquidity. Theory: simulation-bases.md Section 4.1
```

### RuleLLM / `RuleLLMMarketMaker`

```text
Hybrid: MarketMaker rules + LLM reasoning. Theory: simulation-bases.md Section 4.1
```

### Rag / `RagLLMMarketMaker`

```text
RAG-augmented: MarketMaker rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.1
```
