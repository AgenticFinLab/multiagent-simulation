# FramingEffect / Gain Frame Follower

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FramingEffect |
| Agent type | Gain Frame Follower |
| Canonical class | `GainFrameFollower` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: The GainFrameFollower represents retail investors and individual traders who systematically over-weight gain-framed information. When market prices are above fundamental (positive deviation), this investor interprets the information as a gain and responds with risk-averse buying -- purchasing at a size proportional to the deviation, bounded by cash and a 800-share cap. When prices fall below fundamental, this investor sells proportionally to protect the gain. This agent is destabilizing in rising markets (amplifying positive deviations) and partially stabilizing in falling markets (selling reduces overshooting below fundamental).

## Financial Theory / Theoretical Basis

### Rule / `GainFrameFollower`
- Theory: simulation-bases.md Section 4.1 -- GainFrameFollower
- Theoretical basis: Gain frame risk aversion (Tversky & Kahneman, 1981).

### LLM / `LLMGainFrameFollower`
- LLM-driven GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMGainFrameFollower`
- RuleLLM-driven GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMGainFrameFollower`
- RAG-augmented GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| gain_weight | Rule: `1.5` | Rule |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FramingEffect.LLM.prompts:LLM_GAIN_FRAME_FOLLOWER_SYS', 'user_message': 'examples.FramingEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_GAIN_FRAME_FOLLOWER_SYS', 'user_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FramingEffect.Rag.prompts:RAGLLM_GAIN_FRAME_FOLLOWER_SYS', 'user_message': 'examples.FramingEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | gainframefollower | GainFrameFollower | `GainFrameFollower` | 2 | `examples/FramingEffect/Rule/players.py` |
| LLM | gainframefollower | GainFrameFollower | `LLMGainFrameFollower` | 2 | `examples/FramingEffect/LLM/players.py` |
| RuleLLM | gainframefollower | GainFrameFollower | `RuleLLMGainFrameFollower` | 2 | `examples/FramingEffect/RuleLLM/players.py` |
| Rag | gainframefollower | GainFrameFollower | `RagLLMGainFrameFollower` | 2 | `examples/FramingEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 GainFrameFollower

**Summary**: The GainFrameFollower represents retail investors and individual traders who systematically over-weight gain-framed information. When market prices are above fundamental (positive deviation), this investor interprets the information as a gain and responds with risk-averse buying -- purchasing at a size proportional to the deviation, bounded by cash and a 800-share cap. When prices fall below fundamental, this investor sells proportionally to protect the gain. This agent is destabilizing in rising markets (amplifying positive deviations) and partially stabilizing in falling markets (selling reduces overshooting below fundamental).

**Theoretical Foundation**: Kahneman & Tversky (1979) Prospect Theory; gain-frame risk aversion documented by Tversky & Kahneman (1981).

**Activation Scenarios**:

| Market Condition                      | This Investor's Response                   | Economic Effect                                                      | Relevant Theory    |
|---------------------------------------|--------------------------------------------|----------------------------------------------------------------------|--------------------|
| deviation > 0.02 (gain frame active)  | Buy; qty = min(800, int(deviation x 5000)) | Amplifies positive deviation; drives price further above fundamental | Theory 1, Theory 2 |
| deviation < -0.02 (loss frame active) | Sell; qty = min(800, int(                  | deviation                                                            | x 5000))           |
|                                       | deviation                                  | <= 0.02                                                               | Hold               |

**Behavioral Framework**:

- **Information set**: `price`, `deviation` (the framing signal)
- **Core mechanism**: Treats positive deviation as gain (risk-averse buy to capture upside) and negative deviation as loss (sell to cut loss); the decision formula `qty = min(800, int(|deviation| x 5000))` implements proportional-to-framing-intensity trade sizing
- **Mathematical model**:
  ```
  if deviation > 0.02: action = buy, qty = min(800, int(deviation x 5000), cash/price)
  elif deviation < -0.02: action = sell, qty = min(800, int(|deviation| x 5000), position)
  else: hold
  ```

## Source Docstring Excerpts

### Rule / `GainFrameFollower`

```text
Theory: simulation-bases.md Section 4.1 -- GainFrameFollower

Theoretical basis: Gain frame risk aversion (Tversky & Kahneman, 1981).
Overweights gains-framed information; becomes risk-averse when returns are presented as gains.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMGainFrameFollower`

```text
LLM-driven GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMGainFrameFollower`

```text
RuleLLM-driven GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMGainFrameFollower`

```text
RAG-augmented GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md Section 4.1.
```
