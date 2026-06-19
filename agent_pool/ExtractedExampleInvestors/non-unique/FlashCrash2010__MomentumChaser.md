# FlashCrash2010 / Momentum Chaser

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash2010 |
| Agent type | Momentum Chaser |
| Canonical class | `MomentumChaser` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Role:** HFT trend-follower; amplifies directional moves.

## Financial Theory / Theoretical Basis

### Rule / `MomentumChaser`
- Theory: simulation-bases.md Section 4.2 -- MomentumChaser
- Theoretical basis: Positive-feedback trading amplifies directional price

### LLM / `LLMMomentumChaser`
- LLM-driven momentum chaser -- trend amplification via LLM systematic reasoning. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMMomentumChaser`
- Hybrid: Trend-following momentum rules + LLM reasoning. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMMomentumChaser`
- RAG-augmented momentum chaser -- trend-following rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| entry_threshold | Rule: `0.001`<br>LLM: `0.001`<br>RuleLLM: `0.001`<br>Rag: `0.001` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FlashCrash2010.LLM.prompts:LLM_MOMENTUM_CHASER_SYS', 'user_message': 'examples.FlashCrash2010.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_MOMENTUM_CHASER_SYS', 'user_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FlashCrash2010.Rag.prompts:RAGLLM_MOMENTUM_CHASER_SYS', 'user_message': 'examples.FlashCrash2010.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| lookback_window | Rule: `5` | Rule |
| max_size | Rule: `1000`<br>LLM: `1000`<br>RuleLLM: `1000`<br>Rag: `1000` | LLM, Rag, Rule, RuleLLM |
| position_multiplier | Rule: `10000`<br>LLM: `10000`<br>RuleLLM: `10000`<br>Rag: `10000` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentumchaser | MomentumChaser | `MomentumChaser` | 2 | `examples/FlashCrash2010/Rule/players.py` |
| LLM | momentumchaser | MomentumChaser | `LLMMomentumChaser` | 2 | `examples/FlashCrash2010/LLM/players.py` |
| RuleLLM | momentumchaser | MomentumChaser | `RuleLLMMomentumChaser` | 2 | `examples/FlashCrash2010/RuleLLM/players.py` |
| Rag | momentumchaser | MomentumChaser | `RagLLMMomentumChaser` | 2 | `examples/FlashCrash2010/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 MomentumChaser

**Role:** HFT trend-follower; amplifies directional moves.

**Behavioural model:**
```python
velocity = (price_history[-1] - price_history[-lookback]) / price_history[-lookback]
if abs(velocity) > entry_threshold:
    quantity = int(min(abs(velocity) * position_multiplier, 1000))
    quantity = quantity if velocity > 0 else -quantity
else:
    quantity = 0
# constrained by cash (buy) or position (sell)
provides_liquidity: False
agent_type: "hft"
```

**Parameters:** `lookback_window`, `entry_threshold`, `position_multiplier`

**Decision rule:** Enters in the direction of price move if the `lookback_window` return exceeds `entry_threshold`; position size proportional to velocity.

**Market effect:** Adds net sell flow during crash, contributing to HFT participation count and reinforcing the momentum.

**Theory:** De Long et al. (1990) -- positive-feedback speculation.

**Diversity:** Varied `lookback_window` (3-10) and `entry_threshold` (0.005-0.02).

**Distinguishing feature:** Unlike HFTMarketMaker, MomentumChaser always participates in the direction of the trend; `agent_type = "hft"` keeps it counted in `hft_participation`.

---

## Source Docstring Excerpts

### Rule / `MomentumChaser`

```text
HFT momentum chaser - trend-following, amplifies moves.

Theory: simulation-bases.md Section 4.2 -- MomentumChaser
Theoretical basis: Positive-feedback trading amplifies directional price
moves; velocity threshold determines entry, position size scaled by momentum.
See simulation-bases.md Section 4.2 for mathematical model.

Parameters from config extras:
    - initial_cash, initial_position, lookback_window, entry_threshold,
      position_multiplier, custom_state_hot_limit, record_path
```

### LLM / `LLMMomentumChaser`

```text
LLM-driven momentum chaser -- trend amplification via LLM systematic reasoning. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMMomentumChaser`

```text
Hybrid: Trend-following momentum rules + LLM reasoning. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMMomentumChaser`

```text
RAG-augmented momentum chaser -- trend-following rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.2.
```
