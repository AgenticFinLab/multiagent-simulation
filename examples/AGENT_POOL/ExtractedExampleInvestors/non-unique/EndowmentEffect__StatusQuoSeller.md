# EndowmentEffect / Status Quo Seller

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EndowmentEffect |
| Agent type | Status Quo Seller |
| Canonical class | `StatusQuoSeller` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

A status-quo-biased seller who holds positions long due to inertia, demanding a premium significantly above fundamental before selling. Creates a secondary resistance layer below EndowedHolder, reflecting cognitive switching costs rather than pure ownership attachment.

## Financial Theory / Theoretical Basis

### Rule / `StatusQuoSeller`
- Theory: simulation-bases.md Section 4.2 -- StatusQuoSeller
- Theoretical basis: Samuelson & Zeckhauser (1988) status quo bias; inertia

### LLM / `LLMStatusQuoSeller`
- LLM-driven status-quo-biased seller -- inertia and loss aversion modeled via LLM. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMStatusQuoSeller`
- RuleLLM status-quo-biased seller -- inertia rules require large premium before selling. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMStatusQuoSeller`
- RAG-augmented status quo seller -- inertia-driven holding with status quo bias literature. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EndowmentEffect.LLM.prompts:LLM_STATUS_QUO_SELLER_SYS', 'user_message': 'examples.EndowmentEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_STATUS_QUO_SELLER_SYS', 'user_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EndowmentEffect.Rag.prompts:RAG_STATUS_QUO_SELLER_SYS', 'user_message': 'examples.EndowmentEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| status_quo_premium | LLM: `0.2`<br>RuleLLM: `0.2`<br>Rag: `0.2` | LLM, Rag, RuleLLM |
| status_quo_threshold | Rule: `0.2` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | statusquoseller | StatusQuoSeller | `StatusQuoSeller` | 2 | `examples/EndowmentEffect/Rule/players.py` |
| LLM | statusquoseller | StatusQuoSeller | `LLMStatusQuoSeller` | 2 | `examples/EndowmentEffect/LLM/players.py` |
| RuleLLM | statusquoseller | StatusQuoSeller | `RuleLLMStatusQuoSeller` | 2 | `examples/EndowmentEffect/RuleLLM/players.py` |
| Rag | statusquoseller | StatusQuoSeller | `RagLLMStatusQuoSeller` | 2 | `examples/EndowmentEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 StatusQuoSeller

#### 4.2.1 Summary

A status-quo-biased seller who holds positions long due to inertia, demanding a premium significantly above fundamental before selling. Creates a secondary resistance layer below EndowedHolder, reflecting cognitive switching costs rather than pure ownership attachment.

#### 4.2.2 Theoretical and Empirical Foundation

- **Samuelson & Zeckhauser (1988)**: Status quo bias; strong preference for current state even when switching is rational. DOI: `10.1007/BF00055564`.
- **Kahneman, Knetsch & Thaler (1990)**: Endowment effect extends to the broader status quo framing -- ownership makes "not selling" the default. DOI: `10.1086/261737`.

#### 4.2.3 Design Purpose and Activation Scenarios

- **Activates when**: `deviation > status_quo_threshold` -> sells 400 units; `deviation < -0.08` -> buys 300 units
- **Role in phenomenon**: Destabilizing -- creates a second price floor; rarely sells, reinforces overvaluation
- **Interaction effects**: Complements EndowedHolder; forms a two-layer resistance structure that sustains price above fundamental

#### 4.2.4 Behavioral Framework

**Information set**: price, fundamental, deviation

**Mechanism narrative**: StatusQuoSeller holds unless deviation exceeds a large threshold (`status_quo_threshold`), reflecting inertia bias -- they need a compelling reason to trade. This creates intermediate-level resistance below EndowedHolder's threshold. Buys on significant undervaluation to exploit perceived safety.

**Mathematical model**:
```
if deviation > status_quo_threshold: sell(400)
elif deviation < -0.08: buy(300)
else: hold()
```

**Behavioral properties**: High inertia (δ large), moderate loss aversion, infrequent trading, asymmetric sell threshold

#### 4.2.5 Decision Process Walkthrough

1. Receive deviation from market broadcast
2. If deviation > status_quo_threshold -> sell 400 units
3. If deviation < -0.08 -> buy 300 units
4. Otherwise -> hold

#### 4.2.6 Worked Numerical Example

Given: deviation = 0.10, status_quo_threshold = 0.12

- 0.10 < 0.12 -> do NOT sell; 0.10 > -0.08 -> do NOT buy -> **hold**

Given: deviation = 0.15, status_quo_threshold = 0.12

- 0.15 > 0.12 -> **sell 400 units**

#### 4.2.7 Academic References

- Samuelson, W., & Zeckhauser, R. (1988). Status quo bias. *Journal of Risk and Uncertainty*, 1(1), 7-59. DOI: 10.1007/BF00055564
- Kahneman, D. et al. (1990). *Journal of Political Economy*, 98(6). DOI: 10.1086/261737

---

## Source Docstring Excerpts

### Rule / `StatusQuoSeller`

```text
Holds positions too long due to status quo bias, demands premium to sell.

Theory: simulation-bases.md Section 4.2 -- StatusQuoSeller
Theoretical basis: Samuelson & Zeckhauser (1988) status quo bias; inertia
prevents rational rebalancing even at significant overvaluation.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMStatusQuoSeller`

```text
LLM-driven status-quo-biased seller -- inertia and loss aversion modeled via LLM. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMStatusQuoSeller`

```text
RuleLLM status-quo-biased seller -- inertia rules require large premium before selling. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMStatusQuoSeller`

```text
RAG-augmented status quo seller -- inertia-driven holding with status quo bias literature. Theory: simulation-bases.md Section 4.2.
```
