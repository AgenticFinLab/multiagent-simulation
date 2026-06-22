# EndowmentEffect / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EndowmentEffect |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

An uninformed random trader who provides background volume and prevents the market from being trivially predictable. Embodies noise trading theory.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: Black (1986) noise trading and market efficiency; uninformed

### LLM / `LLMNoiseTrader`
- LLM-driven noise trader -- random uninformed trades modeled with probabilistic LLM persona. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM noise trader -- probabilistic trading rules with random direction selection. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented noise trader -- random uninformed trading with noise trading literature. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EndowmentEffect.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.EndowmentEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EndowmentEffect.Rag.prompts:RAG_NOISE_TRADER_SYS', 'user_message': 'examples.EndowmentEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| noise_size | Rule: `150`<br>LLM: `150`<br>RuleLLM: `150`<br>Rag: `150` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 1 | `examples/EndowmentEffect/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 1 | `examples/EndowmentEffect/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 1 | `examples/EndowmentEffect/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 1 | `examples/EndowmentEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

#### 4.5.1 Summary

An uninformed random trader who provides background volume and prevents the market from being trivially predictable. Embodies noise trading theory.

#### 4.5.2 Theoretical and Empirical Foundation

- **Black (1986)**: Noise trading; uninformed traders are essential for liquid markets. DOI: `10.1111/j.1540-6261.1986.tb04513.x`.
- **De Long, Shleifer, Summers & Waldmann (1990)**: Noise trader risk -- noise traders can move prices systematically and earn returns that persist. DOI: `10.1086/261703`.

#### 4.5.3 Design Purpose and Activation Scenarios

- **Activates when**: `random() < trade_probability` each round
- **Role in phenomenon**: Neutral -- provides background volume, prevents degenerate equilibria
- **Interaction effects**: Dilutes clean endowment signals; occasional spurious buys can temporarily amplify overvaluation

#### 4.5.4 Behavioral Framework

**Information set**: none (random)

**Mechanism narrative**: Trades with fixed probability each round; direction and size randomly determined from a uniform distribution.

**Mathematical model**:
```
if random() < trade_probability:
    direction = buy if random() > 0.5 else sell
    quantity = uniform(min_order, max_order)
    submit(direction, quantity)
else: hold()
```

**Behavioral properties**: Uninformed, random, bounded position

#### 4.5.5 Decision Process Walkthrough

1. Random draw vs. trade_probability
2. If trading: random direction (buy/sell) and size (uniform)
3. Submit order or hold

#### 4.5.6 Worked Numerical Example

Given: trade_probability = 0.30, random draw = 0.22 < 0.30 -> trades; direction = buy; size = 10 -> **buy 10 shares**

#### 4.5.7 Academic References

- Black, F. (1986). Noise. *Journal of Finance*, 41(3), 528-543. DOI: 10.1111/j.1540-6261.1986.tb04513.x
- De Long, J. B. et al. (1990). Noise trader risk. *Journal of Political Economy*, 98(4), 703-738. DOI: 10.1086/261703

---

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader providing baseline liquidity.

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical basis: Black (1986) noise trading and market efficiency; uninformed
random trades provide liquidity and prevent trivial equilibria.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader -- random uninformed trades modeled with probabilistic LLM persona. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM noise trader -- probabilistic trading rules with random direction selection. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader -- random uninformed trading with noise trading literature. Theory: simulation-bases.md Section 4.5.
```
