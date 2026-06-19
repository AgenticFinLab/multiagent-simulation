# GameStopShortSqueeze / Momentum Retail

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GameStopShortSqueeze |
| Agent type | Momentum Retail |
| Canonical class | `MomentumRetail` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`MomentumRetail` represents late-arriving FOMO buyers who join after the squeeze is already visible. It is smaller than `RetailCoordinated` but extends the upward pressure.

## Financial Theory / Theoretical Basis

### Rule / `MomentumRetail`
- Theory: simulation-bases.md Section 4.5 -- MomentumRetail
- Theoretical basis: FOMO and momentum trading (Barber & Odean, 2008).

### LLM / `LLMMomentumRetail`
- LLM-driven FOMO momentum retail trader. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMMomentumRetail`
- RuleLLM-driven FOMO momentum retail trader. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMMomentumRetail`
- RagLLM-driven momentum retail trader: chases price momentum without coordination. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fomo_threshold | Rule: `0.05` | Rule |
| fundamental_value | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `300000.0`<br>LLM: `300000.0`<br>RuleLLM: `300000.0`<br>Rag: `300000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_MOMENTUM_RETAIL_SYS', 'user_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_MOMENTUM_RETAIL_SYS', 'user_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAGLLM_MOMENTUM_RETAIL_SYS', 'user_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `300` | Rule |
| min_order | Rule: `50` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentumretail | MomentumRetail | `MomentumRetail` | 2 | `examples/GameStopShortSqueeze/Rule/players.py` |
| LLM | momentumretail | NoiseTrader | `LLMMomentumRetail` | 2 | `examples/GameStopShortSqueeze/LLM/players.py` |
| RuleLLM | momentumretail | NoiseTrader | `RuleLLMMomentumRetail` | 2 | `examples/GameStopShortSqueeze/RuleLLM/players.py` |
| Rag | momentumretail | NoiseTrader | `RagLLMMomentumRetail` | 2 | `examples/GameStopShortSqueeze/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 MomentumRetail

#### Section 4.5.1 Summary

`MomentumRetail` represents late-arriving FOMO buyers who join after the squeeze is already visible. It is smaller than `RetailCoordinated` but extends the upward pressure.

#### Section 4.5.2 Theoretical and Empirical Foundation

The basis is Barber et al. (2022) on retail attention and momentum trading. The agent captures the social-media attention wave after price movement becomes public.

#### Section 4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > fomo_threshold` | buy | late-cycle momentum amplification | Section 2 Theory 3 |
| otherwise | hold | no FOMO signal | Section 2 Theory 3 |

#### Section 4.5.4 Behavioral Framework

```
if deviation > fomo_threshold:
    buy min(50, cash / price)
else:
    hold
```

#### Section 4.5.5 Decision Process Walkthrough

With deviation 8% and `fomo_threshold = 0.05`, the trader buys because the upward move is visible enough to trigger FOMO.

#### Section 4.5.6 Worked Numerical Example

At price 25 and cash 300,000, the affordable quantity exceeds 50, so the small-retail cap binds at 50 shares.

#### Section 4.5.7 Academic References

Barber et al. (2022); Lyocsa et al. (2022).

---

## Source Docstring Excerpts

### Rule / `MomentumRetail`

```text
Theory: simulation-bases.md Section 4.5 -- MomentumRetail

Theoretical basis: FOMO and momentum trading (Barber & Odean, 2008).
FOMO retail trader: buys when price is rising above FOMO threshold.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMMomentumRetail`

```text
LLM-driven FOMO momentum retail trader. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMMomentumRetail`

```text
RuleLLM-driven FOMO momentum retail trader. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMMomentumRetail`

```text
RagLLM-driven momentum retail trader: chases price momentum without coordination. Theory: simulation-bases.md Section 4.5.
```
