# HerdEffect / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HerdEffect |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements De Long et al. (1990) noise trader risk model. Random bid price near market; mean-reverting quantity. Stochastic trigger for emergent herding -- accidental herd initiator.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.4 -- NoiseTrader
- Theoretical basis: Noise trader model (De Long et al., 1990).
- Formula: P ~ N(P_last, sigma²); Q ~ N(0, sigma_qty²) - position x mean_reversion.

### LLM / `LLMNoiseTrader`
- LLM-powered NoiseTrader: random uninformed trading. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMNoiseTrader`
- Hybrid rule+LLM NoiseTrader: random uninformed decisions. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented NoiseTrader: random uninformed trading with retrieved knowledge. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `calculate_bid`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HerdEffect.LLM.prompts:LLM_NOISE_SYS', 'user_message': 'examples.HerdEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_NOISE_SYS', 'user_message': 'examples.HerdEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_NOISE_SYS', 'user_message': 'examples.HerdEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_mean_reversion | Rule: `0.1` | Rule |
| price_noise_std | Rule: `2.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| qty_noise_std | Rule: `5.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | investor_noise | Noise Trader | `NoiseTrader` | 2 | `examples/HerdEffect/Rule/players.py` |
| LLM | llm_noise | LLM Noise Trader | `LLMNoiseTrader` | 2 | `examples/HerdEffect/LLM/players.py` |
| RuleLLM | rulellm_noise | RuleLLM Noise Trader | `RuleLLMNoiseTrader` | 2 | `examples/HerdEffect/RuleLLM/players.py` |
| Rag | ragllm_noise | RAG Noise Trader | `RagLLMNoiseTrader` | 2 | `examples/HerdEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 NoiseTrader

**Summary**: Implements De Long et al. (1990) noise trader risk model. Random bid price near market; mean-reverting quantity. Stochastic trigger for emergent herding -- accidental herd initiator.

**Foundation**: De Long, Shleifer, Summers & Waldmann (1990) noise trader risk. `doi:10.1111/j.1540-6261.1990.tb03695.x`

**Design Purpose**: Provide the random initial price signal that triggers momentum response. Mean-reverting position prevents persistent one-sided positioning while injecting the noise needed to start emergent herding episodes.

**Behavioral Framework**:

| Decision Variable | Logic                       | Formula                                                    |
|-------------------|-----------------------------|------------------------------------------------------------|
| Bid price         | Market price + noise        | `P + N(0, price_noise_std)`                                |
| Quantity          | Random minus mean-reversion | `N(0, qty_noise_std) - position x position_mean_reversion` |
| Position          | Mean-reverting to zero      | Gradual return to neutral                                  |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. `bid_price = P + N(0, price_noise_std)`
3. `qty = N(0, qty_noise_std) - position x position_mean_reversion`
4. Update cash/position; send order

**Worked Example** (price_noise_std=2.0, qty_noise_std=5.0, position_mean_reversion=0.1, P=100, position=5):
- bid_price = 100 + 1.4 = 101.4
- qty = 3.7 - 5 x 0.1 = 3.2 -> 3 shares
- Interpretation: Random positive buy; if r > 0, MomentumInvestor will amplify this next round

**References**: simulation-bases.md Section 2; De Long et al. (1990) `doi:10.1111/j.1540-6261.1990.tb03695.x`

---

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Theory: simulation-bases.md Section 4.4 -- NoiseTrader

Theoretical basis: Noise trader model (De Long et al., 1990).
Formula: P ~ N(P_last, sigma²); Q ~ N(0, sigma_qty²) - position x mean_reversion.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMNoiseTrader`

```text
LLM-powered NoiseTrader: random uninformed trading. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
Hybrid rule+LLM NoiseTrader: random uninformed decisions. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented NoiseTrader: random uninformed trading with retrieved knowledge. Theory: simulation-bases.md Section 4.4.
```
