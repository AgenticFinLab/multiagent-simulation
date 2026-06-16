# CarryTradeUnwind / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CarryTradeUnwind |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The NoiseTrader provides background FX order flow -- representing importers, exporters, portfolio managers, and retail FX participants whose trades are unconnected to carry trade positioning. In FX markets, non-speculative flow accounts for approximately 60-70% of daily volume, providing the liquidity that makes carry trades executable. trade_probability = 0.30 is calibrated to a higher value than BlackMonday1987 (0.05) because FX markets have substantially more non-speculative background activity.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: Noise trader model (Black, 1986); random buy/sell orders

### LLM / `LLMNoiseTrader`
- LLM-driven noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM-driven noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `100000.0`<br>LLM: `100000.0`<br>RuleLLM: `100000.0`<br>Rag: `100000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_NOISE_TRADER_SYS', 'user_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `100.0` | Rule |
| min_order | Rule: `20.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.05` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noise_trader | Noise Trader | `NoiseTrader` | 2 | `examples/CarryTradeUnwind/Rule/players.py` |
| LLM | llm_noise_trader | LLM Noise Trader | `LLMNoiseTrader` | 2 | `examples/CarryTradeUnwind/LLM/players.py` |
| RuleLLM | rulellm_noise_trader | RuleLLM Noise Trader | `RuleLLMNoiseTrader` | 2 | `examples/CarryTradeUnwind/RuleLLM/players.py` |
| Rag | ragllm_noise_trader | RAG Noise Trader | `RagLLMNoiseTrader` | 2 | `examples/CarryTradeUnwind/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

#### 4.5.1  Summary

The NoiseTrader provides background FX order flow -- representing importers, exporters, portfolio managers, and retail FX participants whose trades are unconnected to carry trade positioning. In FX markets, non-speculative flow accounts for approximately 60-70% of daily volume, providing the liquidity that makes carry trades executable. trade_probability = 0.30 is calibrated to a higher value than BlackMonday1987 (0.05) because FX markets have substantially more non-speculative background activity.

#### 4.5.2  Theoretical and Empirical Foundation

**Theory 1: Noise Trading as Market Liquidity (Black)**
- Citation: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. DOI: 10.2307/2328481
- Core Insight: Noise traders are essential for liquidity. trade_probability = 0.30 calibrated to represent non-speculative FX participation. Quantity range [100, 500] represents retail and small institutional lot sizes.

#### 4.5.3  Design Purpose and Activation Scenarios

**Purpose**: Prevent deterministic price paths; model genuine background FX market activity; ensure variance across simulation runs for statistical analysis.

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**: None -- purely random.

**4.5.4.2  Core Behavioral Mechanism**
1. Draw r ~ Uniform(0, 1). If r < 0.30: trade.
2. Draw direction (buy/sell, 50/50); draw quantity ~ Uniform(100, 500).
3. Execute. Hold otherwise.

**4.5.4.3  Mathematical Model**
- P(trade) = 0.30; direction = 50/50; Q ~ Uniform(100, 500)

| Parameter         | Value | Source             |
|-------------------|-------|--------------------|
| trade_probability | 0.30  | Black (1986)       |
| min_order         | 100   | FX market lot size |
| max_order         | 500   | FX market lot size |

**4.5.4.4  Behavioral Properties**: Random, neutral, stochastic.

#### 4.5.5  Decision Process Walkthrough

r = 0.18 < 0.30 -> trade. Direction: buy. Quantity: 300. Order: buy 300 at current price.

#### 4.5.6  Worked Numerical Example

r = 0.65 >= 0.30 -> hold. No order sent.
r = 0.12 < 0.30 -> trade. Direction: sell. Quantity: 210. Order: sell 210 at current FX rate.

#### 4.5.7  Academic References

| # | Citation                                                                              | Notes                                               |
|---|---------------------------------------------------------------------------------------|-----------------------------------------------------|
| 1 | Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. DOI: 10.2307/2328481 | trade_probability calibration; noise trading theory |

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader providing baseline liquidity.

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical basis: Noise trader model (Black, 1986); random buy/sell orders
provide liquidity and baseline variance independent of carry dynamics.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM-driven noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.
```
