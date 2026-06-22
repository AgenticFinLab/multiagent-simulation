# LTCMCollapse / Liquidity Provider

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LTCMCollapse |
| Agent type | Liquidity Provider |
| Canonical class | `LiquidityProvider` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `LiquidityProvider` represents market makers that supply liquidity when deviations are moderate but withdraw when stress becomes large. Its withdrawal is central to the liquidity-black-hole mechanism.

## Financial Theory / Theoretical Basis

### Rule / `LiquidityProvider`
- Theory: simulation-bases.md Section 4.4 -- LiquidityProvider
- Theoretical basis: Morris & Shin (2004) liquidity black holes.

### LLM / `LLMLiquidityProvider`
- Theory: simulation-bases.md Section 4.4 -- LiquidityProvider.

### RuleLLM / `RuleLLMLiquidityProvider`
- Theory: simulation-bases.md Section 4.4 -- LiquidityProvider.

### Rag / `RagLLMLiquidityProvider`
- RAG stress-sensitive liquidity provider. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `1000`<br>LLM: `1000`<br>RuleLLM: `1000`<br>Rag: `1000` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| inventory_limit | Rule: `2000`<br>LLM: `2000`<br>RuleLLM: `2000`<br>Rag: `2000` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LTCMCollapse.LLM.prompts:LLM_LIQUIDITYPROVIDER_PROMPT', 'user_message': 'examples.LTCMCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_LIQUIDITYPROVIDER_PROMPT', 'user_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LTCMCollapse.Rag.prompts:RAG_LIQUIDITYPROVIDER_PROMPT', 'user_message': 'examples.LTCMCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| stress_exit | Rule: `0.4`<br>LLM: `0.4`<br>RuleLLM: `0.4`<br>Rag: `0.4` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | liquidityprovider | LiquidityProvider | `LiquidityProvider` | 2 | `examples/LTCMCollapse/Rule/players.py` |
| LLM | liquidityprovider | LiquidityProvider | `LLMLiquidityProvider` | 2 | `examples/LTCMCollapse/LLM/players.py` |
| RuleLLM | liquidityprovider | LiquidityProvider | `RuleLLMLiquidityProvider` | 2 | `examples/LTCMCollapse/RuleLLM/players.py` |
| Rag | liquidityprovider | LiquidityProvider | `RagLLMLiquidityProvider` | 2 | `examples/LTCMCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 LiquidityProvider

#### Section 4.4.1 Summary

The `LiquidityProvider` represents market makers that supply liquidity when deviations are moderate but withdraw when stress becomes large. Its withdrawal is central to the liquidity-black-hole mechanism.

#### Section 4.4.2 Theoretical and Empirical Foundation

The design follows Morris & Shin's liquidity black-hole mechanism (Section 2.4). Liquidity provision is conditionally stabilizing and disappears in stressed deviations.

#### Section 4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) > 0.05` | Hold | Withdraws liquidity under stress | Section 2.4 |
| `abs(position) < inventory_limit` and `deviation > 0` | Sell up to 500 | Mean-reversion supply | Section 2.4 |
| `abs(position) < inventory_limit` and `deviation <= 0` | Buy up to 500/cash limit | Mean-reversion demand | Section 2.4 |

#### Section 4.4.4 Behavioral Framework

The stress trigger is `abs(deviation) > 0.05`; the inventory cap is `inventory_limit`. Normal-market size is capped at 500 shares per round.

#### Section 4.4.5 Decision Process Walkthrough

If deviation is -2% and inventory room remains, the agent buys. If deviation is -7%, it withdraws and holds.

#### Section 4.4.6 Worked Numerical Example

With inventory limit 2,000 and current position 1,000, inventory room is 1,000. The per-round cap binds at 500 shares.

#### Section 4.4.7 Academic References

Morris & Shin (2004); Brunnermeier & Pedersen (2009).

## Source Docstring Excerpts

### Rule / `LiquidityProvider`

```text
Provides market liquidity under normal conditions but withdraws under stress.

Theory: simulation-bases.md Section 4.4 -- LiquidityProvider
Theoretical basis: Morris & Shin (2004) liquidity black holes.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMLiquidityProvider`

```text
LLM-driven stress-sensitive liquidity provider.

Theory: simulation-bases.md Section 4.4 -- LiquidityProvider.
```

### RuleLLM / `RuleLLMLiquidityProvider`

```text
RuleLLM stress-sensitive liquidity provider.

Theory: simulation-bases.md Section 4.4 -- LiquidityProvider.
```

### Rag / `RagLLMLiquidityProvider`

```text
RAG stress-sensitive liquidity provider. Theory: simulation-bases.md Section 4.4.
```
