# GameStopShortSqueeze / Market Maker Gamma

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GameStopShortSqueeze |
| Agent type | Market Maker Gamma |
| Canonical class | `MarketMakerGamma` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`MarketMakerGamma` represents options market makers who must buy the underlying stock as price rises in order to hedge short-call gamma exposure.

## Financial Theory / Theoretical Basis

### Rule / `MarketMakerGamma`
- Theory: simulation-bases.md Section 4.3 -- MarketMakerGamma
- Theoretical basis: Gamma squeeze dynamics (Jarrow & Li, 2021).

### LLM / `LLMMarketMakerGamma`
- LLM-driven gamma-hedging market maker. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMMarketMakerGamma`
- RuleLLM-driven gamma-hedging market maker. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMMarketMakerGamma`
- RagLLM-driven market maker with gamma hedging: delta-hedges options exposure. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| gamma_exposure | Rule: `0.3` | Rule |
| initial_cash | Rule: `3000000.0`<br>LLM: `3000000.0`<br>RuleLLM: `3000000.0`<br>Rag: `3000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_MARKET_MAKER_GAMMA_SYS', 'user_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_MARKET_MAKER_GAMMA_SYS', 'user_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAGLLM_MARKET_MAKER_GAMMA_SYS', 'user_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | marketmakergamma | MarketMakerGamma | `MarketMakerGamma` | 1 | `examples/GameStopShortSqueeze/Rule/players.py` |
| LLM | marketmakergamma | MarketMakerGamma | `LLMMarketMakerGamma` | 1 | `examples/GameStopShortSqueeze/LLM/players.py` |
| RuleLLM | marketmakergamma | MarketMakerGamma | `RuleLLMMarketMakerGamma` | 1 | `examples/GameStopShortSqueeze/RuleLLM/players.py` |
| Rag | marketmakergamma | MarketMakerGamma | `RagLLMMarketMakerGamma` | 1 | `examples/GameStopShortSqueeze/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 MarketMakerGamma

#### Section 4.3.1 Summary

`MarketMakerGamma` represents options market makers who must buy the underlying stock as price rises in order to hedge short-call gamma exposure.

#### Section 4.3.2 Theoretical and Empirical Foundation

The basis is Jarrow and Li (2021) on short-squeeze risk and Hu et al. (2021) on options-flow amplification in the GameStop episode.

#### Section 4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > 0` | buy hedge quantity | mechanical gamma amplification | Section 2 Theory 2 |
| otherwise | hold | no positive-delta hedge need | Section 2 Theory 2 |

#### Section 4.3.4 Behavioral Framework

```
hedge_qty = int(abs(deviation) * gamma_exposure * 5000)
if deviation > 0:
    buy min(hedge_qty, cash / price)
else:
    hold
```

#### Section 4.3.5 Decision Process Walkthrough

With deviation 20% and `gamma_exposure = 0.3`, hedge demand is `int(0.20 * 0.3 * 5000) = 300` shares.

#### Section 4.3.6 Worked Numerical Example

At price 30 with sufficient cash, the market maker buys 300 shares, adding to the upward price impact.

#### Section 4.3.7 Academic References

Jarrow & Li (2021); Hu et al. (2021).

## Source Docstring Excerpts

### Rule / `MarketMakerGamma`

```text
Theory: simulation-bases.md Section 4.3 -- MarketMakerGamma

Theoretical basis: Gamma squeeze dynamics (Jarrow & Li, 2021).
Market maker delta-hedging options exposure: buys more when price rises.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMMarketMakerGamma`

```text
LLM-driven gamma-hedging market maker. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMMarketMakerGamma`

```text
RuleLLM-driven gamma-hedging market maker. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMMarketMakerGamma`

```text
RagLLM-driven market maker with gamma hedging: delta-hedges options exposure. Theory: simulation-bases.md Section 4.3.
```
