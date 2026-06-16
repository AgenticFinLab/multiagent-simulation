# FramingEffect / Loss Frame Reactor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FramingEffect |
| Agent type | Loss Frame Reactor |
| Canonical class | `LossFrameReactor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: The LossFrameReactor represents investors who over-weight loss-framed information, becoming risk-seeking when facing potential losses. The behavioral pattern is paradoxically similar to GainFrameFollower in action direction (both buy on positive deviation, sell on negative), but the underlying motivation differs: LossFrameReactor is driven by risk-seeking under loss (convex value function) rather than gain-chasing. In aggregate, both agents reinforce trends, making them jointly destabilizing.

## Financial Theory / Theoretical Basis

### Rule / `LossFrameReactor`
- Theory: simulation-bases.md Section 4.2 -- LossFrameReactor
- Theoretical basis: Loss frame risk seeking (Tversky & Kahneman, 1981).

### LLM / `LLMLossFrameReactor`
- LLM-driven LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMLossFrameReactor`
- RuleLLM-driven LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMLossFrameReactor`
- RAG-augmented LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FramingEffect.LLM.prompts:LLM_LOSS_FRAME_REACTOR_SYS', 'user_message': 'examples.FramingEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_LOSS_FRAME_REACTOR_SYS', 'user_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FramingEffect.Rag.prompts:RAGLLM_LOSS_FRAME_REACTOR_SYS', 'user_message': 'examples.FramingEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| loss_weight | Rule: `1.8` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | lossframereactor | LossFrameReactor | `LossFrameReactor` | 2 | `examples/FramingEffect/Rule/players.py` |
| LLM | lossframereactor | LossFrameReactor | `LLMLossFrameReactor` | 2 | `examples/FramingEffect/LLM/players.py` |
| RuleLLM | lossframereactor | LossFrameReactor | `RuleLLMLossFrameReactor` | 2 | `examples/FramingEffect/RuleLLM/players.py` |
| Rag | lossframereactor | LossFrameReactor | `RagLLMLossFrameReactor` | 2 | `examples/FramingEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 LossFrameReactor

**Summary**: The LossFrameReactor represents investors who over-weight loss-framed information, becoming risk-seeking when facing potential losses. The behavioral pattern is paradoxically similar to GainFrameFollower in action direction (both buy on positive deviation, sell on negative), but the underlying motivation differs: LossFrameReactor is driven by risk-seeking under loss (convex value function) rather than gain-chasing. In aggregate, both agents reinforce trends, making them jointly destabilizing.

**Theoretical Foundation**: Tversky & Kahneman (1981) loss frame risk-seeking; Kuhberger (1998) meta-analysis confirming loss-frame effects in financial contexts.

**Activation Scenarios**:

| Market Condition  | This Investor's Response               | Economic Effect              |
|-------------------|----------------------------------------|------------------------------|
| deviation > 0.02  | Buy; same formula as GainFrameFollower | Amplifies upward deviation   |
| deviation < -0.02 | Sell; same formula                     | Amplifies downward deviation |
| Hold zone         | Hold                                   | Neutral                      |

## Source Docstring Excerpts

### Rule / `LossFrameReactor`

```text
Theory: simulation-bases.md Section 4.2 -- LossFrameReactor

Theoretical basis: Loss frame risk seeking (Tversky & Kahneman, 1981).
Overweights loss-framed information; becomes risk-seeking when presented with potential losses.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMLossFrameReactor`

```text
LLM-driven LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMLossFrameReactor`

```text
RuleLLM-driven LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMLossFrameReactor`

```text
RAG-augmented LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md Section 4.2.
```
